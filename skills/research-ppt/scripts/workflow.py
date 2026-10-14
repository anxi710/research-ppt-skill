#!/usr/bin/env python3
"""Preparation, production handoff, and independent acceptance for research PPTs.

No model calls, PPT production, automatic review approval, or external publishing.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import math
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from decktools import sha256, load, write, under, audit_pptx

PREP = ['brief.json', 'analysis/evidence.json', 'analysis/figure_manifest.json',
        'design/style_profile.json', 'design/slide_plan.json']
CHECKS = ['visual', 'facts', 'sources', 'notes', 'crop_completeness']
KINDS = {'source_claim','author_interpretation','presenter_analysis','illustration'}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def positive(value: Any) -> bool:
    return type(value) in (int,float) and math.isfinite(value) and value > 0


def init(args: argparse.Namespace) -> int:
    root=args.project.resolve()
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise ValueError('Initialize into a new/empty private workspace.')
    if not positive(args.minutes): raise ValueError('minutes must be positive and finite')
    paths=[p.resolve() for p in args.source]
    if any(not p.is_file() for p in paths): raise ValueError('Every source must exist')
    if args.template and not args.template.is_file(): raise ValueError('Template not found')
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
    brief={'language':args.language,'audience':args.audience,'target_minutes':args.minutes,
           'qa_time_included':False,'purpose':'research_talk','sections':[],
           'sources':sources,'assumptions':[],'research_connection':None,
           'confidentiality':'private_workspace','backend_preference':'ppt-master'}
    write(root/'brief.json',brief)
    write(root/'analysis/evidence.json',{'claims':[]})
    write(root/'analysis/figure_manifest.json',{'figures':[]})
    write(root/'design/style_profile.json',{'name':'project-style','review_status':'pending','basis':''})
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
    if not nonempty(brief.get('audience')):errors.append('Audience missing')
    if not nonempty(brief.get('language')):errors.append('Language missing')
    if not positive(brief.get('target_minutes')):errors.append('Time budget missing/invalid')
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
    slides=data['design/slide_plan.json'].get('slides',[]);slide_ids=set();seconds=0
    if not slides:errors.append('Slide plan is empty')
    for slide in slides:
        sid=slide.get('id')
        if not nonempty(sid) or sid in slide_ids:errors.append('Invalid/duplicate slide ID')
        slide_ids.add(sid)
        for key in ['topic','question','takeaway','speaker_notes']:
            if not nonempty(slide.get(key)):errors.append(f'{sid}: {key} missing')
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
        if len(slide.get('on_slide_text',[]))>4:warnings.append(f'{sid}: check display-text density')
    if positive(brief.get('target_minutes')) and abs(seconds-60*brief['target_minutes'])>max(60,brief['target_minutes']*6):
        errors.append('Visible-slide timing differs materially from the requested budget; revise plan or brief')
    return {'status':'fail' if errors else 'pass','errors':errors,'warnings':warnings,
            'planned_seconds':seconds,'slides':len(slides),'meaning':'Metadata and provenance preflight; agent still judges evidence and design.'}


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
    _,renders=render_entries(args.pptx,args.render_report,len(plan))
    if args.out.exists():raise ValueError('Refuse to overwrite a review; use a new review filename')
    rows=[]
    for n,(slide,render) in enumerate(zip(plan,renders),1):
        image=(args.render_report.parent/'pages'/render['file']).resolve()
        import os
        rows.append({'slide':n,'slide_id':slide['id'],'render_path':os.path.relpath(image,args.out.parent.resolve()),
                     'render_sha256':render['sha256'],**{key:'pending' for key in CHECKS},'comments':''})
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
        for key in CHECKS:
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
    s=subs.add_parser('init');s.add_argument('--project',type=Path,required=True);s.add_argument('--source',type=Path,action='append',required=True);s.add_argument('--template',type=Path);s.add_argument('--minutes',type=float,required=True);s.add_argument('--language',required=True);s.add_argument('--audience',required=True);s.set_defaults(func=init)
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
