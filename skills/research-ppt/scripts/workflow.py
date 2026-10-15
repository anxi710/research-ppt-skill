#!/usr/bin/env python3
"""Preparation, production handoff, and independent acceptance for research PPTs.

No model calls, PPT production, automatic review approval, or external publishing.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import json
import math
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Any

from decktools import sha256, load, write, under, audit_pptx

PREP = ['brief.json', 'analysis/evidence.json', 'analysis/figure_manifest.json',
        'design/style_profile.json', 'design/slide_plan.json']
CHECKS = ['visual', 'facts', 'sources', 'notes', 'crop_completeness']
COMMUNICATION_CHECKS = ['audience_copy', 'reference_match']
CITATION_PLACEMENTS = {'compact_footer', 'notes', 'per_slide'}
KINDS = {'source_claim','author_interpretation','presenter_analysis','illustration'}
INTAKE_FIELDS = ['audience','target_minutes','qa_time_included','qa_minutes','language','purpose',
                 'sections','style_intent','deliverables']
PRESENTATION_CHOICES = {
    'presentation_type': {'research_report','paper_talk','literature_review','progress_report','method_tutorial'},
    'detail_level': {'overview','standard','detailed'},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def positive(value: Any) -> bool:
    return type(value) in (int,float) and math.isfinite(value) and value > 0


def communication_contract_errors(style: dict) -> list[str]:
    """Version the optional communication rules without invalidating legacy styles."""
    if 'communication_contract' not in style:return []
    contract=style['communication_contract']
    if not isinstance(contract,dict):return ['Style: communication_contract must be an object']
    errors=[]
    if type(contract.get('version')) is not int or contract.get('version')!=1:
        errors.append('Style: communication_contract version must be 1')
    placement=contract.get('citation_placement')
    if not isinstance(placement,str) or placement not in CITATION_PLACEMENTS:
        errors.append('Style: communication_contract citation_placement must be compact_footer, notes or per_slide')
    rules=contract.get('rules')
    if not isinstance(rules,list) or not rules or any(not nonempty(rule) for rule in rules):
        errors.append('Style: communication_contract rules must be a nonempty list of nonempty strings')
    return errors


def review_checks(style: dict) -> list[str]:
    contract=style.get('communication_contract')
    versioned=(isinstance(contract,dict) and type(contract.get('version')) is int
               and contract['version']==1)
    return CHECKS+COMMUNICATION_CHECKS if versioned else list(CHECKS)


def intake_requirements(brief: dict) -> dict:
    """Snapshot user-facing choices, excluding later evidence/design review details."""
    result={key:brief.get(key) for key in INTAKE_FIELDS}
    # Preserve accepted legacy briefs that predate these choices without rewriting them.
    result.update({key:brief[key] for key in PRESENTATION_CHOICES if key in brief})
    result['sources']=[{key:src.get(key) for key in ['id','sha256','role']}
                       for src in brief.get('sources',[])]
    return copy.deepcopy(result)


def intake_errors(brief: dict, *, require_confirmation: bool=True) -> list[str]:
    errors=[]
    for key,choices in PRESENTATION_CHOICES.items():
        if key in brief and (not isinstance(brief[key],str) or brief[key] not in choices):
            errors.append(f'Intake: invalid {key}; choose from {", ".join(sorted(choices))}')
    for key in ['audience','language','purpose','style_intent']:
        if not nonempty(brief.get(key)):errors.append(f'Intake: {key} missing')
    if not positive(brief.get('target_minutes')):errors.append('Intake: time budget missing/invalid')
    if type(brief.get('qa_time_included')) is not bool:
        errors.append('Intake: specify whether the time includes Q&A')
    qa_minutes=brief.get('qa_minutes')
    if brief.get('qa_time_included') is True:
        if not positive(qa_minutes) or (positive(brief.get('target_minutes')) and qa_minutes>=brief['target_minutes']):
            errors.append('Intake: Q&A minutes must be positive and less than the total time')
    elif type(qa_minutes) not in (int,float) or qa_minutes!=0:
        errors.append('Intake: Q&A minutes must be zero when excluded from the time budget')
    for key in ['sections','deliverables']:
        value=brief.get(key)
        if not isinstance(value,list) or any(not nonempty(item) for item in value):
            errors.append(f'Intake: {key} must be a list of nonempty strings')
        elif key=='deliverables' and not value:errors.append('Intake: deliverables missing')
    if require_confirmation:
        record=brief.get('intake_confirmation')
        if not isinstance(record,dict) or record.get('status') not in {'confirmed','delegated'}:
            errors.append('Intake: user confirmation or explicit delegation is pending')
        else:
            if not nonempty(record.get('user_response')):
                errors.append('Intake: actual user response or message reference missing')
            if record.get('requirements')!=intake_requirements(brief):
                errors.append('Intake: requirements changed; summarize and confirm the changes')
    return errors


def intake(args: argparse.Namespace) -> int:
    """Prepare a pending summary; never infer or manufacture user confirmation."""
    path=args.project.resolve()/'brief.json';brief=load(path)
    errors=intake_errors(brief,require_confirmation=False)
    if errors:raise ValueError('; '.join(errors))
    requirements=intake_requirements(brief)
    record=brief.get('intake_confirmation',{})
    # Reprinting a current record must not erase an actual response.
    current=(isinstance(record,dict) and record.get('requirements')==requirements
             and record.get('status') in {'confirmed','delegated'}
             and nonempty(record.get('user_response')))
    if not current:
        record={'status':'pending','user_response':'','requirements':requirements}
        brief['intake_confirmation']=record;write(path,brief)
    print(json.dumps(record,ensure_ascii=False,indent=2))
    print('Present a readable summary to the user. Record only an actual confirmation or explicit delegation; this command does not obtain consent.')
    return 0


def project_basename(value: str) -> str:
    """Keep a readable Unicode name within one portable path component."""
    name=re.sub(r'[\W_]+','-',unicodedata.normalize('NFKC',value),flags=re.UNICODE)
    name=name.strip('-').lower()[:64].rstrip('-') or 'research-talk'
    if re.fullmatch(r'con|prn|aux|nul|com[0-9]|lpt[0-9]',name):name='talk-'+name
    return name


def init(args: argparse.Namespace) -> int:
    if not positive(args.minutes): raise ValueError('minutes must be positive and finite')
    presentation={'presentation_type':getattr(args,'presentation_type','research_report'),
                  'detail_level':getattr(args,'detail_level','detailed')}
    for key,value in presentation.items():
        if not isinstance(value,str) or value not in PRESENTATION_CHOICES[key]:
            raise ValueError(f'Invalid {key}')
    paths=[p.resolve() for p in args.source]
    if any(not p.is_file() for p in paths): raise ValueError('Every source must exist')
    if args.template and not args.template.is_file(): raise ValueError('Template not found')
    name=project_basename(getattr(args,'name',None) or paths[0].stem)
    project=getattr(args,'project',None)
    if project is not None:
        root=project.resolve()
        if root.exists() and (not root.is_dir() or any(root.iterdir())):
            raise ValueError('Initialize into a new/empty private workspace.')
    else:
        # Reserve a new directory atomically; even an empty existing talk is kept.
        output_root=(Path.cwd()/'outputs').resolve();base=name;number=1
        while True:
            root=output_root/name
            try:
                root.mkdir(parents=True)
                break
            except FileExistsError:
                number+=1;name=f'{base}-{number:02d}'
    for d in ['inputs','analysis','assets/paper','design','notes','handoff','production','qa','exports']:
        (root/d).mkdir(parents=True,exist_ok=True)
    sources=[]
    for n,path in enumerate(paths,1):
        dest=root/'inputs'/f'source_{n:02d}{path.suffix.lower()}'
        shutil.copy2(path,dest)
        sources.append({'id':f'S{n}','path':str(dest.relative_to(root)),
                        'original_name':path.name,'sha256':sha256(dest),
                        'version':'Specify the exact supplied version','role':'research_source'})
    if args.template:
        dest=root/'inputs'/('template'+args.template.suffix.lower());shutil.copy2(args.template,dest)
        sources.append({'id':'STYLE','path':str(dest.relative_to(root)),
                        'original_name':args.template.name,'sha256':sha256(dest),'role':'style_reference'})
    brief={**presentation,'project_name':name,
           'output_files':{'pptx':f'exports/{name}.pptx','pdf':f'exports/{name}-preview.pdf',
                           'speaker_notes':f'exports/{name}-notes.md'},
           'language':args.language,'audience':args.audience,'target_minutes':args.minutes,
           'qa_time_included':None,'qa_minutes':0,'purpose':'research_talk','sections':[],
           'style_intent':'','deliverables':['pptx','pdf','speaker_notes'],
           'intake_confirmation':{'status':'pending','user_response':'','requirements':{}},
           'sources':sources,'assumptions':[],'research_connection':None,
           'confidentiality':'private_workspace','backend_preference':'ppt-master'}
    write(root/'brief.json',brief)
    write(root/'analysis/evidence.json',{'claims':[]})
    write(root/'analysis/figure_manifest.json',{'figures':[]})
    write(root/'design/style_profile.json',{
        'name':'project-style','review_status':'pending','basis':'',
        'communication_contract':{
            'version':1,'citation_placement':'compact_footer',
            'rules':[
                'Use display_title and on_slide_text as the exact audience-facing copy; planning fields are not automatically visible.',
                'Write concise titles and explanations that the intended audience can understand; keep presentation instructions in speaker notes.',
                'Match the reviewed reference style and its communication choices when a reference is supplied; otherwise follow the recorded style basis.',
                'Keep scientific conditions, uncertainty and meaningful qualifiers visible where needed to understand the claim; citation placement does not remove them.'
            ]}})
    write(root/'design/slide_plan.json',{'slides':[]})
    write(root/'state.json',{'stage':'intake','created_at':now(),'accepted_artifacts':[],
                              'open_issues':[],'review_status':'not_started'})
    print(root)
    return 0


def preflight_report(root: Path) -> dict:
    errors=[];warnings=[];data={}
    for name in PREP:
        try: data[name]=load(root/name)
        except (OSError,ValueError) as exc: errors.append(f'{name}: {exc}')
    if errors: return {'status':'fail','errors':errors,'warnings':warnings}
    brief=data['brief.json'];sources=brief.get('sources',[]);source_ids=set()
    errors.extend(intake_errors(brief))
    if not sources:errors.append('No source inventory')
    for src in sources:
        sid=src.get('id')
        if not nonempty(sid) or sid in source_ids:errors.append('Invalid/duplicate source ID')
        source_ids.add(sid)
        if src.get('role') != 'style_reference' and (not nonempty(src.get('version')) or src['version'].startswith('Specify')):
            errors.append(f'Source {sid}: exact version not recorded')
        try:
            path=under(root,src.get('path',''))
            if not path.is_file() or sha256(path)!=src.get('sha256'):errors.append(f'Source {sid}: missing/changed bytes')
        except (ValueError,OSError):errors.append(f'Source {sid}: invalid local path')
    claims=data['analysis/evidence.json'].get('claims',[]);claim_ids=set()
    if not claims:errors.append('Evidence ledger is empty')
    for claim in claims:
        cid=claim.get('id')
        if not nonempty(cid) or cid in claim_ids:errors.append('Invalid/duplicate claim ID')
        claim_ids.add(cid)
        if claim.get('kind') not in KINDS:errors.append(f'{cid}: invalid claim kind')
        if not nonempty(claim.get('statement')):errors.append(f'{cid}: statement missing')
        if claim.get('review_status')!='verified':errors.append(f'{cid}: evidence not reviewed')
        refs=claim.get('source_ids',[])
        if any(s not in source_ids for s in refs):errors.append(f'{cid}: unknown source reference')
        if claim.get('kind')!='illustration' and (not refs or not nonempty(claim.get('locator'))):
            errors.append(f'{cid}: factual/analytical claim lacks source locator')
        if claim.get('unresolved_blocker'):errors.append(f'{cid}: unresolved evidence blocker')
    assets=data['analysis/figure_manifest.json'].get('figures',[]);asset_ids=set()
    for asset in assets:
        fid=asset.get('id')
        if not nonempty(fid) or fid in asset_ids:errors.append('Invalid/duplicate figure ID')
        asset_ids.add(fid)
        if asset.get('source_id') and asset['source_id'] not in source_ids:errors.append(f'{fid}: unknown source')
        if asset.get('kind') in {'original_figure','source_table'} and not asset.get('source_id'):
            errors.append(f'{fid}: original evidence asset lacks source ID')
        if asset.get('review_status')!='verified':errors.append(f'{fid}: crop/asset review pending')
        for cid in asset.get('evidence_ids',[]):
            if cid not in claim_ids:errors.append(f'{fid}: unknown evidence {cid}')
        try:
            path=under(root,asset.get('path',''))
            if not path.is_file() or sha256(path)!=asset.get('sha256'):errors.append(f'{fid}: missing/changed asset')
        except (ValueError,OSError):errors.append(f'{fid}: invalid asset path')
    style=data['design/style_profile.json']
    if style.get('review_status')!='verified' or not nonempty(style.get('basis')):
        errors.append('Style not reviewed or decision basis missing')
    errors.extend(communication_contract_errors(style))
    has_communication_contract='communication_contract' in style
    communication_contract=style.get('communication_contract')
    slides=data['design/slide_plan.json'].get('slides',[]);slide_ids=set();seconds=0;display_text_metrics=[]
    if not slides:errors.append('Slide plan is empty')
    for slide in slides:
        sid=slide.get('id')
        if not nonempty(sid) or sid in slide_ids:errors.append('Invalid/duplicate slide ID')
        slide_ids.add(sid)
        for key in ['topic','question','takeaway','speaker_notes']:
            if not nonempty(slide.get(key)):errors.append(f'{sid}: {key} missing')
        if has_communication_contract and not nonempty(slide.get('display_title')):
            errors.append(f'{sid}: display_title missing (planning fields are not display copy)')
        if has_communication_contract:
            display_copy=slide.get('on_slide_text')
            if not isinstance(display_copy,list) or any(not nonempty(block) for block in display_copy):
                errors.append(f'{sid}: on_slide_text must be an explicit list of nonempty strings (empty list allowed for visual-only slides)')
            if isinstance(communication_contract,dict) and communication_contract.get('citation_placement')=='per_slide':
                placement=slide.get('citation_placement')
                if not isinstance(placement,str) or placement not in {'compact_footer','notes'}:
                    errors.append(f'{sid}: per_slide citation policy requires citation_placement compact_footer or notes')
        if type(slide.get('hidden')) is not bool:errors.append(f'{sid}: hidden must be boolean')
        if not positive(slide.get('seconds')):errors.append(f'{sid}: positive duration required')
        elif not slide.get('hidden'):seconds+=slide['seconds']
        if not slide.get('evidence_ids'):errors.append(f'{sid}: evidence link required (illustrations permitted)')
        for cid in slide.get('evidence_ids',[]):
            if cid not in claim_ids:errors.append(f'{sid}: unknown evidence {cid}')
        visual=slide.get('primary_visual',{})
        if not nonempty(visual.get('type')) or not nonempty(visual.get('description')):
            errors.append(f'{sid}: core visual not specified')
        if visual.get('type') in {'original_figure','source_table'} and not visual.get('asset_ids'):
            errors.append(f'{sid}: evidence visual missing its asset')
        for fid in visual.get('asset_ids',[]):
            if fid not in asset_ids:errors.append(f'{sid}: unknown visual {fid}')
        if not slide.get('reading_order'):errors.append(f'{sid}: reading order missing')
        title=slide.get('display_title','')
        title_characters=len(title) if isinstance(title,str) else 0
        blocks=slide.get('on_slide_text',[])
        if not isinstance(blocks,list):blocks=[]
        display_text_metrics.append({'slide_id':sid,'title_characters':title_characters,
                                     'total_characters':title_characters+sum(len(block) for block in blocks if isinstance(block,str)),
                                     'text_block_count':len(blocks)})
    speaking_minutes=brief.get('target_minutes')
    if positive(speaking_minutes) and brief.get('qa_time_included') is True and positive(brief.get('qa_minutes')):
        speaking_minutes-=brief['qa_minutes']
    if positive(speaking_minutes) and abs(seconds-60*speaking_minutes)>max(60,speaking_minutes*6):
        errors.append('Visible-slide timing differs materially from the speaking budget (excluding reserved Q&A); revise plan or brief')
    return {'status':'fail' if errors else 'pass','errors':errors,'warnings':warnings,
            'planned_seconds':seconds,'slides':len(slides),'display_text_metrics':display_text_metrics,
            'meaning':'Metadata and provenance preflight; display text metrics are informational, not density approval. Agent still judges evidence and design.'}


def preflight(args: argparse.Namespace) -> int:
    report=preflight_report(args.project.resolve());write(args.out,report)
    print(json.dumps(report,ensure_ascii=False,indent=2));return int(report['status']!='pass')


def handoff(args: argparse.Namespace) -> int:
    root=args.project.resolve();report=preflight_report(root)
    if report['status']!='pass':raise ValueError('Preparation not ready: '+'; '.join(report['errors']))
    run_id=args.run_id or datetime.now(timezone.utc).strftime('run-%Y%m%dT%H%M%S%fZ')
    if not re.fullmatch(r'[A-Za-z0-9_-]+',run_id):raise ValueError('Unsafe run ID')
    dest=root/'handoff'/run_id
    if dest.exists():raise ValueError('Handoffs are immutable; use a new run ID')
    dest.mkdir(parents=True)
    fingerprints={}
    for name in PREP:
        target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/name,target);fingerprints[name]=sha256(target)
    resources={}
    for item in load(root/'brief.json')['sources']+load(root/'analysis/figure_manifest.json')['figures']:
        resources[item['path']]=sha256(under(root,item['path']))
    manifest={'schema_version':'1','created_at':now(),'workspace':str(root),
              'preparation':fingerprints,'resources':resources}
    write(dest/'manifest.json',manifest)
    text=f'''# Research production handoff\n\nPrivate workspace: `{root}`\nContract manifest: `{dest/'manifest.json'}`\n\nRead all five preparation snapshots in this directory. Use the referenced original\nsource/asset files in the private workspace, preserving their hashes and figure identity.\nThey are local references, not permission to upload/publish them.\n\nUse the current, real ppt-master checkout and its current documented route. Map this\nbrief into its current runtime; do not invent CLI flags or forge confirmation gates.\nDo not change claims, durations, page roster or figure meaning silently. Raise needed\ncontract changes to preparation before production. Work under `{root/'production'}`.\n\nReturn a real PPTX and a completed build receipt listing actual backend revision,\ncommands, outputs and limitations. Native text/annotations remain editable; original\npaper charts remain source images. Include notes, citations and true hidden flags.\nThe final PPTX will be independently rendered and checked against this contract.\n'''
    brief=load(root/'brief.json')
    text+='\n## Audience-facing copy\n\n'
    text+=('Use each slide\'s `display_title` and `on_slide_text` as the exact display copy when supplied. '
           'Layout, line breaks and mathematically equivalent typesetting may be adjusted. '
           'Changed wording requires updated preparation and a fresh handoff. '
           'The `topic`, `question`, `takeaway`, `reading_order` and `speaker_notes` fields guide planning '
           'or speaking; they are not automatically visible text. Do not turn planning instructions '
           'into audience-facing labels. Legacy plans without `display_title` retain their accepted design.\n\n'
           'Preserve meaningful scientific qualifiers, conditions and uncertainty on the slide wherever '
           'they are necessary to interpret its claim, even when bibliographic citations are placed in notes.\n')
    style=load(root/'design/style_profile.json')
    if 'communication_contract' in style:
        text+='\n## Communication contract\n\n'
        text+='```json\n'+json.dumps(style['communication_contract'],ensure_ascii=False,indent=2)+'\n```\n\n'
        text+=('Apply every communication rule and the citation placement policy above. Independent review '
               'must check `audience_copy` against the planned display copy and `reference_match` against '
               'the supplied reference or recorded style basis; neither is approved by metadata or text counts.\n')
    presentation={key:brief[key] for key in PRESENTATION_CHOICES if key in brief}
    if presentation:
        text+='\n## Presentation scope\n\n```json\n'
        text+=json.dumps(presentation,ensure_ascii=False,indent=2)+'\n```\n\n'
        text+=('Preserve the accepted report narrative, explanatory depth, source distinctions '
               'and any coverage record in the slide plan. Keep detailed speaker notes and '
               'planned hidden backups within the agreed speaking budget.\n')
    outputs={key:path for key,path in brief.get('output_files',{}).items()
             if key in brief.get('deliverables',[])}
    if outputs:
        text+='\n## Delivery paths\n\nRequested paths relative to the private workspace:\n\n'
        text+='```json\n'+json.dumps(outputs,ensure_ascii=False,indent=2)+'\n```\n\n'
        text+=('Keep backend build files under production/. Place delivery candidates at these paths '
               'before final hashing, rendering and review. Preserve existing versions; use a new '
               'version filename for revisions and record the actual paths in the build receipt.\n')
    (dest/'handoff.md').write_text(text,encoding='utf-8')
    receipt=load(Path(__file__).resolve().parents[1]/'templates/build_receipt.example.json')
    receipt['handoff_manifest_sha256']=sha256(dest/'manifest.json')
    write(dest/'build_receipt.template.json',receipt)
    print(dest);return 0


def contract_errors(project: Path, handoff_dir: Path) -> list[str]:
    manifest=load(handoff_dir/'manifest.json');errors=[]
    if set(manifest.get('preparation',{}))!=set(PREP):errors.append('Incomplete preparation snapshot')
    for name,digest in manifest.get('preparation',{}).items():
        for base in [project,handoff_dir]:
            path=under(base,name)
            if not path.is_file() or sha256(path)!=digest:errors.append(f'Changed contract: {name}')
    for name,digest in manifest.get('resources',{}).items():
        path=under(project,name)
        if not path.is_file() or sha256(path)!=digest:errors.append(f'Changed source/asset: {name}')
    return errors


def render_entries(pptx: Path, report_path: Path, count: int) -> tuple[dict, list[dict]]:
    report=load(report_path)
    if report.get('source_pptx_sha256')!=sha256(pptx):raise ValueError('Stale PPTX render')
    if report.get('includes_hidden') is not True:raise ValueError('All-slide QA must include hidden slides')
    if report.get('slide_mapping')!=list(range(1,count+1)):raise ValueError('Render/slide mapping mismatch')
    rows=report.get('renders',[])
    if len(rows)!=count or sorted(r.get('pdf_page',0) for r in rows)!=list(range(1,count+1)):
        raise ValueError('Render roster incomplete')
    for row in rows:
        path=under(report_path.parent/'pages',row['file'])
        if not path.is_file() or sha256(path)!=row.get('sha256'):raise ValueError('Missing/stale render image')
    return report, sorted(rows,key=lambda r:r['pdf_page'])


def review_init(args: argparse.Namespace) -> int:
    root=args.project.resolve();handoff_dir=args.handoff.resolve()
    errors=contract_errors(root,handoff_dir)
    if errors:raise ValueError('; '.join(errors))
    plan=load(root/'design/slide_plan.json')['slides']
    checks=review_checks(load(root/'design/style_profile.json'))
    _,renders=render_entries(args.pptx,args.render_report,len(plan))
    if args.out.exists():raise ValueError('Refuse to overwrite a review; use a new review filename')
    rows=[]
    for n,(slide,render) in enumerate(zip(plan,renders),1):
        image=(args.render_report.parent/'pages'/render['file']).resolve()
        import os
        rows.append({'slide':n,'slide_id':slide['id'],'render_path':os.path.relpath(image,args.out.parent.resolve()),
                     'render_sha256':render['sha256'],**{key:'pending' for key in checks},'comments':''})
    write(args.out,{'pptx_sha256':sha256(args.pptx),
                    'handoff_manifest_sha256':sha256(handoff_dir/'manifest.json'),
                    'render_report_sha256':sha256(args.render_report),
                    'reviewer':'','review_mode':'pending','slides':rows,'unresolved_blockers':[]})
    print(f'{args.out}: every check is pending; open and inspect actual pages before approval.')
    return 0


def gate(args: argparse.Namespace) -> int:
    root=args.project.resolve();errors=contract_errors(root,args.handoff.resolve())
    prep=preflight_report(root)
    errors+=prep['errors']
    checks=review_checks(load(root/'design/style_profile.json'))
    plan=root/'design/slide_plan.json';rows=load(plan)['slides'];digest=sha256(args.pptx)
    machine=load(args.audit);review=load(args.review);receipt=load(args.receipt)
    # Recompute inexpensive package checks instead of trusting an arbitrary "pass" flag.
    actual=audit_pptx(args.pptx,plan)
    errors+=actual['errors']
    if machine.get('pptx_sha256')!=digest or machine.get('plan_sha256')!=sha256(plan):errors.append('Machine audit stale')
    if machine.get('machine_status')!='pass':errors.append('Machine audit failed')
    if review.get('pptx_sha256')!=digest:errors.append('Review stale')
    mh=sha256(args.handoff/'manifest.json')
    if review.get('handoff_manifest_sha256')!=mh:errors.append('Review uses another contract')
    if review.get('render_report_sha256')!=sha256(args.render_report):errors.append('Review uses another render report')
    if not nonempty(review.get('reviewer')) or review.get('review_mode') not in {'agent_visual','human','independent_agent'}:
        errors.append('Actual reviewer/mode required')
    try: _,renders=render_entries(args.pptx,args.render_report,actual['slides'])
    except (ValueError,OSError,KeyError) as exc:errors.append(str(exc));renders=[]
    review_rows=review.get('slides',[])
    if sorted(r.get('slide',0) for r in review_rows)!=list(range(1,actual['slides']+1)):
        errors.append('Review must cover every slide exactly once')
    for item in review_rows:
        n=item.get('slide',0)
        if type(n) is not int or not 1<=n<=len(rows):errors.append('Invalid review slide');continue
        if item.get('slide_id')!=rows[n-1]['id']:errors.append(f'Slide {n}: plan ID mismatch')
        for key in checks:
            if item.get(key)!='pass':errors.append(f'Slide {n}: {key} not passed')
        if not nonempty(item.get('comments')):errors.append(f'Slide {n}: review observations missing')
        path=(args.review.parent/item.get('render_path','')).resolve()
        if not path.is_relative_to(root):errors.append(f'Slide {n}: review image outside workspace');continue
        if not path.is_file() or sha256(path)!=item.get('render_sha256'):errors.append(f'Slide {n}: stale reviewed image')
        if renders and (item.get('render_sha256')!=renders[n-1]['sha256'] or path!=(args.render_report.parent/'pages'/renders[n-1]['file']).resolve()):
            errors.append(f'Slide {n}: image not from the actual PPTX render')
    if review.get('unresolved_blockers'):errors.append('Unresolved blockers remain')
    if receipt.get('status')!='completed' or receipt.get('handoff_manifest_sha256')!=mh:
        errors.append('Backend receipt incomplete or wrong contract')
    for key in ['backend_name','backend_path','backend_revision']:
        if not nonempty(receipt.get(key)):errors.append(f'Backend receipt missing {key}')
    if not receipt.get('commands_executed') or not receipt.get('documents_read'):
        errors.append('Backend execution/document provenance missing')
    if receipt.get('pptx_sha256')!=digest:errors.append('Backend receipt PPTX hash stale/missing')
    report={'status':'fail' if errors else 'pass','pptx_sha256':digest,
            'handoff_manifest_sha256':mh,'errors':errors,'warnings':actual['warnings'],
            'meaning':'Record/provenance consistency gate, not a proof of reviewer judgment.'}
    write(args.out,report);print(json.dumps(report,ensure_ascii=False,indent=2));return int(bool(errors))


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    s=subs.add_parser('init');s.add_argument('--project',type=Path,help='Explicit workspace; default: outputs/<name> under the current working directory');s.add_argument('--name',help='Short topic name summarized by the agent; falls back to the first source filename');s.add_argument('--source',type=Path,action='append',required=True);s.add_argument('--template',type=Path);s.add_argument('--minutes',type=float,required=True);s.add_argument('--language',required=True);s.add_argument('--audience',required=True);s.set_defaults(func=init)
    s.add_argument('--presentation-type',choices=sorted(PRESENTATION_CHOICES['presentation_type']),default='research_report',help='Proposed presentation type for intake; default: research_report')
    s.add_argument('--detail-level',choices=sorted(PRESENTATION_CHOICES['detail_level']),default='detailed',help='Proposed depth for intake; default: detailed')
    s=subs.add_parser('intake',help='Prepare a pending requirements summary; does not confirm it');s.add_argument('--project',type=Path,required=True);s.set_defaults(func=intake)
    s=subs.add_parser('preflight');s.add_argument('--project',type=Path,required=True);s.add_argument('--out',type=Path,required=True);s.set_defaults(func=preflight)
    s=subs.add_parser('handoff');s.add_argument('--project',type=Path,required=True);s.add_argument('--run-id');s.set_defaults(func=handoff)
    s=subs.add_parser('review-init');
    for name in ['project','pptx','handoff','render-report','out']:s.add_argument('--'+name,type=Path,required=True)
    s.set_defaults(func=review_init)
    s=subs.add_parser('gate');
    for name in ['project','pptx','handoff','render-report','audit','review','receipt','out']:s.add_argument('--'+name,type=Path,required=True)
    s.set_defaults(func=gate)
    return p

if __name__=='__main__':
    try:
        args=parser().parse_args();raise SystemExit(args.func(args))
    except (ValueError,OSError,KeyError,TypeError,RuntimeError,ImportError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
