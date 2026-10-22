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
SKILL_ROOT = Path(__file__).resolve().parents[1]
BUILTIN_TEMPLATE_ROOT = SKILL_ROOT/'assets/academic-navigator'
BUILTIN_TEMPLATE_SPEC = 'templates/design_spec.deck.academic-navigator.md'
DESIGN_MODES = {'academic_navigator','user_override'}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def positive(value: Any) -> bool:
    return type(value) in (int,float) and math.isfinite(value) and value > 0


def navigation_layout(style: dict) -> dict | None:
    """Budget one left-aligned tab group; old profiles retain their accepted geometry."""
    navigation=style.get('section_navigation')
    if not isinstance(navigation,dict) or 'width_mode' not in navigation:return None
    if navigation['width_mode']!='content':
        raise ValueError('section_navigation width_mode must be content when supplied')
    if navigation.get('enabled') is not True:return None
    sections=navigation.get('sections');gap=navigation.get('tab_gap_px')
    if (not isinstance(sections,list) or not sections
            or any(not isinstance(section,dict) or not nonempty(section.get('id'))
                   or not nonempty(section.get('label')) for section in sections)):
        raise ValueError('section_navigation content width requires sections with IDs and labels')
    if not positive(gap):raise ValueError('section_navigation content width requires positive tab_gap_px')
    typography=style.get('typography');roles=typography.get('roles') if isinstance(typography,dict) else None
    role=roles.get('navigation') if isinstance(roles,dict) else None
    size=role.get('font_size_px') if isinstance(role,dict) else None
    if not positive(size):raise ValueError('section_navigation content width requires a positive navigation font_size_px')
    labels=[f'{i:02d} {section["label"]}' for i,section in enumerate(sections,1)]
    if any(any(char in label for char in '\r\n\t') for label in labels):
        raise ValueError('section_navigation content labels must fit on one line')
    # shortcut: character budgets are not font metrics; use backend measurement and final renders to confirm fit.
    widths=[sum(0 if unicodedata.combining(char) else
                1 if unicodedata.east_asian_width(char) in {'W','F'} else 0.65
                for char in label)*size for label in labels]
    budget=max(widths)+48
    if not math.isfinite(budget) or budget>1184:
        raise ValueError('section_navigation content width exceeds 1184 px; shorten labels or reduce sections without shrinking fonts')
    width=max(128,math.ceil(budget/8)*8)
    total=len(sections)*width+(len(sections)-1)*gap
    if total>1184:
        raise ValueError('section_navigation content width exceeds 1184 px; shorten labels or reduce sections without shrinking fonts')
    left=48
    return {'source':'section_navigation.sections and typography.roles.navigation',
            'reference_canvas':{'width':1280,'height':720},
            'width_budget_note':'Align the group with the title at x48 and leave unused space on the right. Character widths reserve space; verify the actual font and final PPTX render. Scale all coordinates with the canvas.',
            'font_size_px':size,'padding_x_px':24,'tab_gap_px':gap,
            'group':{'x':left,'y':20,'width':total,'height':44},
            'tabs':[{'section_id':section['id'],'text':label,'x':left+i*(width+gap),'y':20,
                     'width':width,'height':44,'text_x':left+i*(width+gap)+width/2,'text_y':48}
                    for i,(section,label) in enumerate(zip(sections,labels))]}


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


def review_checks(style: dict, assets: list[dict] | None = None) -> list[str]:
    contract=style.get('communication_contract')
    versioned=(isinstance(contract,dict) and type(contract.get('version')) is int
               and contract['version']==1)
    checks=CHECKS+COMMUNICATION_CHECKS if versioned else list(CHECKS)
    if 'figure_policy' in style or any('display_region' in item or 'caption_policy' in item for item in assets or []):
        checks.append('figure_framing')
    if isinstance(style.get('section_navigation'),dict) and style['section_navigation'].get('enabled') is True:
        checks.append('section_navigation')
    if isinstance(style.get('typography'),dict) and 'roles' in style['typography']:
        checks.append('typography_consistency')
    if 'palette_policy' in style:checks.append('palette_consistency')
    if 'page_chrome' in style:checks.append('page_chrome')
    if isinstance(style.get('content_grouping'),dict) and style['content_grouping'].get('enabled') is True:
        checks.append('content_grouping')
    if any(item.get('kind')=='context_illustration' for item in assets or []):
        checks.append('external_visual_provenance')
    if isinstance(style.get('design_contract'),dict) and style['design_contract'].get('mode')=='academic_navigator':
        checks.extend(['template_application','projection_readability'])
    return checks


def template_files(root: Path, spec: str) -> dict[str, Path]:
    """Only the bundled, synthetic design specification and SVG prototypes travel."""
    spec_path=under(root,spec)
    if not spec_path.is_file():raise ValueError('Template specification is missing')
    files={spec:spec_path}
    for path in sorted(root.rglob('*.svg')):
        relative=str(path.relative_to(root))
        checked=under(root,relative)
        if not checked.is_file():raise ValueError('Template SVG is missing')
        files[relative]=checked
    if len(files)<2:raise ValueError('Template package has no SVG prototypes')
    return files


def design_contract_errors(brief: dict, style: dict, *, template_snapshot: Path | None=None) -> list[str]:
    """New jobs cannot silently downgrade to a legacy or unresolved design profile."""
    if 'design_contract_version' not in brief and 'design_mode' not in brief:return []
    errors=[];contract=style.get('design_contract')
    if type(brief.get('design_contract_version')) is not int or brief['design_contract_version']!=1:
        errors.append('Design contract: brief design_contract_version must be 1')
    if (not isinstance(contract,dict) or type(contract.get('version')) is not int
            or contract.get('version')!=1 or not isinstance(contract.get('mode'),str)
            or contract.get('mode') not in DESIGN_MODES):
        return errors+['Design contract: style requires version 1 and mode academic_navigator or user_override']
    if 'design_mode' in brief and brief['design_mode']!=contract['mode']:
        errors.append('Design contract: brief design_mode must match style design_contract.mode')
    if contract['mode']=='user_override':
        override=contract.get('override')
        if not isinstance(override,dict) or not all(nonempty(override.get(key)) for key in ['reason','user_instruction']):
            errors.append('Design contract: user_override requires reason and actual user_instruction')
        else:
            record=brief.get('intake_confirmation',{})
            accepted=[brief.get('style_intent',''),record.get('user_response','') if isinstance(record,dict) else '']
            if not any(override['user_instruction'] in text for text in accepted if isinstance(text,str)):
                errors.append('Design contract: user_override instruction must be quoted in the accepted brief or actual intake response')
        return errors
    required=['communication_contract','figure_policy','section_navigation','typography',
              'palette_policy','page_chrome','content_grouping','external_visuals','template_reference']
    for key in required:
        if not isinstance(style.get(key),dict):errors.append(f'Design contract: default requires {key}')
    figure=style.get('figure_policy',{})
    if not isinstance(figure,dict) or figure.get('display_region')!='body_only' or figure.get('caption_policy')!='notes_only':
        errors.append('Design contract: default requires body-only figures and notes-only captions')
    navigation=style.get('section_navigation',{})
    if not isinstance(navigation,dict) or navigation.get('enabled') is not True or navigation.get('active_indicator')!='fill_only':
        errors.append('Design contract: default requires enabled fill-only section navigation')
    if not isinstance(navigation,dict) or navigation.get('scope')!='main_talk' or not positive(navigation.get('tab_gap_px')):
        errors.append('Design contract: default navigation requires scope main_talk and positive tab_gap_px')
    typography=style.get('typography',{})
    roles=typography.get('roles',{}) if isinstance(typography,dict) else {}
    if not isinstance(roles,dict) or not all(key in roles for key in ['cover','title','body','annotation','footer','navigation']):
        errors.append('Design contract: default requires all fixed typography roles including cover and navigation')
    elif any(not isinstance(role,dict) or not nonempty(role.get('font_family')) or not positive(role.get('font_size_px')) for role in roles.values()):
        errors.append('Design contract: fixed typography roles require font_family and positive font_size_px')
    palette=style.get('palette_policy',{})
    if (not isinstance(palette,dict) or type(palette.get('max_accent_colors')) is not int
            or palette.get('max_accent_colors')!=1 or not isinstance(palette.get('accent_colors'),list)
            or len(palette['accent_colors'])!=1):
        errors.append('Design contract: default requires exactly one native accent color')
    chrome=style.get('page_chrome',{})
    number=chrome.get('page_number',{}) if isinstance(chrome,dict) else {}
    if (not isinstance(chrome,dict) or not isinstance(chrome.get('cover'),dict)
            or chrome['cover'].get('title_information_only') is not True
            or not isinstance(number,dict) or number.get('format')!='current'
            or number.get('position')!='bottom_right' or number.get('background') is not True
            or not isinstance(chrome.get('title_separator'),dict)
            or chrome['title_separator'].get('enabled') is not True):
        errors.append('Design contract: default requires information-only cover, current-page badge and body title separator')
    grouping=style.get('content_grouping',{})
    if (not isinstance(grouping,dict) or grouping.get('enabled') is not True
            or grouping.get('same_role_consistency') is not True
            or not isinstance(grouping.get('spacing'),dict)
            or not all(positive(grouping['spacing'].get(key)) for key in ['min_gap_px','padding_px'])):
        errors.append('Design contract: default requires consistent semantic grouping and explicit positive gaps/padding')
    external=style.get('external_visuals',{})
    if not isinstance(external,dict) or type(external.get('enabled')) is not bool:
        errors.append('Design contract: default requires an explicit external_visuals decision')
    reference=style.get('template_reference',{})
    if not isinstance(reference,dict) or reference.get('status')!='selected' or reference.get('kind')!='deck':
        errors.append('Design contract: select the built-in deck template before handoff; pending_default is unresolved')
    else:
        try:
            if (not nonempty(reference.get('root')) or Path(reference['root']).resolve()!=BUILTIN_TEMPLATE_ROOT.resolve()
                    or reference.get('spec')!=BUILTIN_TEMPLATE_SPEC):
                raise ValueError('Default template must reference the actual built-in Academic Navigator package')
            template_files(template_snapshot or BUILTIN_TEMPLATE_ROOT,BUILTIN_TEMPLATE_SPEC)
        except (ValueError,OSError) as exc:errors.append(f'Design contract: {exc}')
    return errors


def visual_style_errors(style: dict, slides: list[dict]) -> list[str]:
    """Validate optional design instructions, not their visual execution in a deck."""
    errors=[]
    policy=style.get('figure_policy')
    if 'figure_policy' in style:
        if not isinstance(policy,dict) or policy.get('display_region')!='body_only' or policy.get('caption_policy')!='notes_only':
            errors.append('Style: figure_policy requires display_region body_only and caption_policy notes_only')
    navigation=style.get('section_navigation')
    if 'section_navigation' in style:
        if not isinstance(navigation,dict) or type(navigation.get('enabled')) is not bool:
            errors.append('Style: section_navigation requires boolean enabled')
        elif (not isinstance(navigation.get('active_indicator','fill_only'),str)
              or navigation.get('active_indicator','fill_only') not in {'fill_only','reference_defined'}):
            errors.append('Style: section_navigation active_indicator must be fill_only or reference_defined')
        elif navigation['enabled']:
            sections=navigation.get('sections');section_ids=set()
            if not isinstance(sections,list) or not sections:
                errors.append('Style: section_navigation sections must be a nonempty ordered list')
            else:
                for section in sections:
                    if not isinstance(section,dict) or not nonempty(section.get('id')) or not nonempty(section.get('label')):
                        errors.append('Style: section_navigation sections require nonempty id and label');continue
                    if section['id'] in section_ids:errors.append('Style: duplicate section_navigation section ID')
                    section_ids.add(section['id'])
            exempt=navigation.get('exempt_slide_ids',[])
            if not isinstance(exempt,list) or any(not nonempty(sid) for sid in exempt):
                errors.append('Style: section_navigation exempt_slide_ids must be a list of slide IDs');exempt=[]
            elif len(set(exempt))!=len(exempt) or any(sid not in {s.get('id') for s in slides} for sid in exempt):
                errors.append('Style: section_navigation has duplicate/unknown exempt slide IDs')
            for slide in slides:
                required=not slide.get('hidden') and slide.get('id') not in exempt
                if (required or 'section_id' in slide) and (not nonempty(slide.get('section_id')) or slide['section_id'] not in section_ids):
                    errors.append(f'{slide.get("id")}: section_id must reference section_navigation sections')
            contract=style.get('design_contract')
            if isinstance(contract,dict) and contract.get('mode')=='academic_navigator':
                used={slide['section_id'] for slide in slides if not slide.get('hidden')
                      and slide.get('id') not in exempt and nonempty(slide.get('section_id'))}
                for sid in sorted(section_ids-used):
                    errors.append(f'Style: main_talk navigation section {sid!r} has no visible non-exempt slide')
    try:navigation_layout(style)
    except ValueError as exc:errors.append(f'Style: {exc}')
    typography=style.get('typography')
    if isinstance(typography,dict) and 'roles' in typography:
        roles=typography['roles']
        required=['title','body','annotation','footer']
        if isinstance(navigation,dict) and navigation.get('enabled') is True:required.append('navigation')
        if not isinstance(roles,dict):errors.append('Style: typography roles must be an object')
        else:
            for name in required:
                role=roles.get(name)
                if not isinstance(role,dict) or not nonempty(role.get('font_family')) or not positive(role.get('font_size_px')):
                    errors.append(f'Style: typography role {name} requires font_family and positive font_size_px')
    palette=style.get('palette_policy')
    if 'palette_policy' in style:
        if not isinstance(palette,dict):errors.append('Style: palette_policy must be an object')
        else:
            colors=palette.get('accent_colors');limit=palette.get('max_accent_colors')
            valid_colors=(isinstance(colors,list) and all(isinstance(c,str) and re.fullmatch(r'#[0-9A-Fa-f]{6}',c) for c in colors))
            if not valid_colors:errors.append('Style: palette_policy accent_colors must be a list of #RRGGBB colors')
            elif len({c.lower() for c in colors})!=len(colors):errors.append('Style: palette_policy accent colors must be unique')
            if type(limit) is not int or limit<0:errors.append('Style: palette_policy max_accent_colors must be a nonnegative integer')
            elif valid_colors and len(colors)>limit:errors.append('Style: palette_policy accent colors exceed the declared limit')
    chrome=style.get('page_chrome')
    if 'page_chrome' in style:
        if not isinstance(chrome,dict) or not any(key in chrome for key in ['cover','page_number','title_separator']):
            errors.append('Style: page_chrome requires cover, page_number or title_separator instructions')
        else:
            if 'cover' in chrome:
                cover=chrome['cover']
                if not isinstance(cover,dict) or cover.get('title_information_only') is not True:
                    errors.append('Style: page_chrome cover requires title_information_only true')
                else:
                    ids=cover.get('slide_ids');visible_ids={s.get('id') for s in slides if not s.get('hidden')}
                    if not isinstance(ids,list) or not ids or any(not nonempty(sid) for sid in ids):
                        errors.append('Style: page_chrome cover slide_ids must be a nonempty list of slide IDs')
                    elif len(set(ids))!=len(ids) or any(sid not in visible_ids for sid in ids):
                        errors.append('Style: page_chrome cover slide_ids must be unique visible slide IDs')
            if 'page_number' in chrome:
                number=chrome['page_number']
                if (not isinstance(number,dict) or number.get('format')!='current'
                        or number.get('position')!='bottom_right' or type(number.get('background')) is not bool):
                    errors.append('Style: page_chrome page_number requires format current, position bottom_right and boolean background')
            if 'title_separator' in chrome:
                separator=chrome['title_separator']
                if not isinstance(separator,dict) or type(separator.get('enabled')) is not bool:
                    errors.append('Style: page_chrome title_separator requires boolean enabled')
    grouping=style.get('content_grouping')
    if 'content_grouping' in style:
        if not isinstance(grouping,dict) or type(grouping.get('enabled')) is not bool:
            errors.append('Style: content_grouping requires boolean enabled')
        elif grouping['enabled']:
            treatments=grouping.get('treatments')
            if (not isinstance(treatments,list) or not treatments
                    or any(not isinstance(item,str) or item not in {'cards','numbered_blocks'} for item in treatments)
                    or len(set(treatments))!=len(treatments)):
                errors.append('Style: content_grouping treatments must be a nonempty unique list of cards or numbered_blocks')
        if isinstance(grouping,dict):
            if 'same_role_consistency' in grouping and type(grouping['same_role_consistency']) is not bool:
                errors.append('Style: content_grouping same_role_consistency must be boolean')
            if 'spacing' in grouping:
                spacing=grouping['spacing']
                if (not isinstance(spacing,dict)
                        or any(not positive(spacing.get(key)) for key in ['min_gap_px','padding_px'])):
                    errors.append('Style: content_grouping spacing requires positive min_gap_px and padding_px')
    external=style.get('external_visuals')
    if 'external_visuals' in style:
        if not isinstance(external,dict) or type(external.get('enabled')) is not bool:
            errors.append('Style: external_visuals requires boolean enabled')
        elif external['enabled']:
            purposes=external.get('purposes')
            if (not isinstance(purposes,list) or not purposes
                    or any(not isinstance(p,str) or p not in {'background','benchmark_context'} for p in purposes)
                    or len(set(purposes))!=len(purposes)):
                errors.append('Style: external_visuals purposes must be a unique list of background or benchmark_context')
            if external.get('claim_boundary')!='context_only' or external.get('source_scope_precedence') is not True:
                errors.append('Style: external_visuals requires claim_boundary context_only and source_scope_precedence true')
    return errors


def external_visual_errors(assets: list[dict], sources: list[dict], style: dict) -> list[str]:
    """Keep sourced teaching images separate from the report's empirical evidence."""
    errors=[];policy=style.get('external_visuals');source_map={src.get('id'):src for src in sources}
    for asset in assets:
        if asset.get('kind')!='context_illustration':continue
        fid=asset.get('id');refs=asset.get('source_ids')
        if (not isinstance(refs,list) or not refs or any(not nonempty(sid) for sid in refs)
                or len(set(refs))!=len(refs) or any(sid not in source_map for sid in refs)):
            errors.append(f'{fid}: context_illustration requires known unique source_ids')
        elif any(source_map[sid].get('role')=='style_reference' for sid in refs):
            errors.append(f'{fid}: context_illustration needs content sources, not style-only references')
        if not nonempty(asset.get('source_locator')):
            errors.append(f'{fid}: context_illustration requires source_locator')
        if asset.get('usage')!='context_only':
            errors.append(f'{fid}: context_illustration usage must be context_only')
        purpose=asset.get('purpose')
        if not isinstance(purpose,str) or purpose not in {'background','benchmark_context'}:
            errors.append(f'{fid}: context_illustration purpose must be background or benchmark_context')
        if isinstance(policy,dict):
            if policy.get('enabled') is False:
                errors.append(f'{fid}: external visuals are disabled by the accepted style')
            elif isinstance(policy.get('purposes'),list) and purpose not in policy['purposes']:
                errors.append(f'{fid}: context_illustration purpose is outside external_visuals policy')
    return errors


def valid_bbox(box: Any) -> bool:
    return (isinstance(box,list) and len(box)==4
            and all(type(v) in (int,float) and math.isfinite(v) for v in box)
            and 0<=box[0]<box[2] and 0<=box[1]<box[3])


def figure_framing_errors(root: Path, assets: list[dict], style: dict) -> list[str]:
    """Check body/context provenance; captions and scientific legends need visual review."""
    errors=[];policy=style.get('figure_policy')
    policy=policy if isinstance(policy,dict) else {}
    for asset in assets:
        if asset.get('kind') not in {'original_figure','source_table'}:continue
        fid=asset.get('id');region=asset.get('display_region',policy.get('display_region'))
        caption=asset.get('caption_policy',policy.get('caption_policy'))
        if region is None and caption is None:continue  # Existing manifests remain valid.
        if region!='body_only' or caption!='notes_only':
            errors.append(f'{fid}: body-only framing requires display_region body_only and caption_policy notes_only')
        provenance=asset.get('caption_provenance')
        if not isinstance(provenance,dict) or not all(nonempty(provenance.get(key)) for key in ['text','locator']):
            errors.append(f'{fid}: caption_provenance requires original caption text and locator')
        context=asset.get('context')
        if not isinstance(context,dict):errors.append(f'{fid}: body-only asset requires independent context');continue
        # Standalone image sources have no PDF page or point-coordinate system.
        # Once either side declares PDF provenance, require the complete pair.
        pdf_located=any(key in record for record in [asset,context] for key in ['pdf_page','bbox_pt'])
        if pdf_located:
            for field in ['bbox_pt','pdf_page']:
                value=asset.get(field)
                if field=='bbox_pt' and not valid_bbox(value):errors.append(f'{fid}: body-only asset requires valid bbox_pt')
                if field=='pdf_page' and (type(value) is not int or value<1):errors.append(f'{fid}: body-only asset requires positive pdf_page')
            if type(context.get('pdf_page')) is not int or context.get('pdf_page')!=asset.get('pdf_page'):
                errors.append(f'{fid}: context must reference the display asset PDF page')
            outer=context.get('bbox_pt');inner=asset.get('bbox_pt')
            if not valid_bbox(outer):errors.append(f'{fid}: context requires valid bbox_pt')
            elif valid_bbox(inner) and not (outer[0]<=inner[0] and outer[1]<=inner[1] and outer[2]>=inner[2] and outer[3]>=inner[3]):
                errors.append(f'{fid}: display bbox lies outside its context bbox')
        try:
            path=under(root,context.get('path',''))
            if not path.is_file() or sha256(path)!=context.get('sha256'):
                errors.append(f'{fid}: missing/changed context asset')
            if path==under(root,asset.get('path','')):errors.append(f'{fid}: context must be separate from the display asset')
        except (ValueError,OSError,TypeError):errors.append(f'{fid}: invalid context asset path')
    return errors


def intake_requirements(brief: dict) -> dict:
    """Snapshot user-facing choices, excluding later evidence/design review details."""
    result={key:brief.get(key) for key in INTAKE_FIELDS}
    # Preserve accepted legacy briefs that predate these choices without rewriting them.
    result.update({key:brief[key] for key in PRESENTATION_CHOICES if key in brief})
    for key in ['design_contract_version','design_mode']:
        if key in brief:result[key]=brief[key]
    result['sources']=[{key:src.get(key) for key in ['id','sha256','role']}
                       for src in brief.get('sources',[])]
    return copy.deepcopy(result)


def intake_errors(brief: dict, *, require_confirmation: bool=True) -> list[str]:
    errors=[]
    if 'design_mode' in brief and (not isinstance(brief['design_mode'],str) or brief['design_mode'] not in DESIGN_MODES):
        errors.append('Intake: invalid design_mode; choose academic_navigator or user_override')
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
    brief={**presentation,'design_contract_version':1,'project_name':name,
           'design_mode':'user_override' if args.template else 'academic_navigator',
           'output_files':{'pptx':f'exports/{name}.pptx','pdf':f'exports/{name}-preview.pdf',
                           'speaker_notes':f'exports/{name}-notes.md'},
           'language':args.language,'audience':args.audience,'target_minutes':args.minutes,
           'qa_time_included':None,'qa_minutes':0,'purpose':'research_talk','sections':[],
           'style_intent':('' if args.template else
                           'Apply the built-in Academic Navigator deck template, including its prototypes, navigation, typography and page chrome.'),
           'deliverables':['pptx','pdf','speaker_notes'],
           'intake_confirmation':{'status':'pending','user_response':'','requirements':{}},
           'sources':sources,'assumptions':[],'research_connection':None,
           'confidentiality':'private_workspace','backend_preference':'ppt-master'}
    write(root/'brief.json',brief)
    write(root/'analysis/evidence.json',{'claims':[]})
    write(root/'analysis/figure_manifest.json',{'figures':[]})
    # New workspaces start from the skill's presentation baseline. Navigation
    # awaits the actual section plan; examples must not invent that plan.
    example=load(Path(__file__).resolve().parents[1]/'templates/style_profile.example.json')
    defaults={key:example[key] for key in ['canvas','typography','palette','figure_policy',
                                         'palette_policy','page_chrome','content_grouping','external_visuals']}
    defaults['section_navigation']={'enabled':True,'sections':[],'exempt_slide_ids':['P01'],
                                   'active_indicator':example['section_navigation']['active_indicator'],
                                   'scope':'main_talk','tab_gap_px':16,'width_mode':'content'}
    if not args.template:
        defaults['template_reference']={
            'kind':'deck',
            'root':str(BUILTIN_TEMPLATE_ROOT.resolve()),
            'spec':BUILTIN_TEMPLATE_SPEC,
            'status':'selected','applied':False}
    write(root/'design/style_profile.json',{
        **defaults,'name':'academic-navigator','review_status':'pending',
        'design_contract':({'version':1,'mode':'user_override','override':{'reason':'','user_instruction':''}}
                           if args.template else {'version':1,'mode':'academic_navigator'}),
        'basis':'Built-in academic-navigator baseline; adapt to source content and any supplied reference.',
        'communication_contract':{
            'version':1,'citation_placement':'compact_footer',
            'rules':[
                'Use display_title and on_slide_text as the exact audience-facing copy; planning fields are not automatically visible.',
                'Write concise titles and explanations that the intended audience can understand; keep presentation instructions in speaker notes.',
                'Match the reviewed reference style and its communication choices when a reference is supplied; otherwise follow the recorded style basis.',
                'Keep scientific conditions, uncertainty and meaningful qualifiers visible where needed to understand the claim; citation placement does not remove them.'
            ]}})
    write(root/'design/slide_plan.json',{'slides':[]})
    print(root)
    return 0


def preflight_report(root: Path, *, template_snapshot: Path | None=None) -> dict:
    errors=[];warnings=[];data={}
    for name in PREP:
        try: data[name]=load(root/name)
        except (OSError,ValueError) as exc: errors.append(f'{name}: {exc}')
    if errors: return {'status':'fail','errors':errors,'warnings':warnings}
    brief=data['brief.json'];sources=brief.get('sources',[]);source_ids=set()
    errors.extend(intake_errors(brief))
    outputs=brief.get('output_files',{});output_paths=set()
    if not isinstance(outputs,dict):errors.append('Delivery: output_files must be an object')
    else:
        for kind,relative in outputs.items():
            if not nonempty(kind) or not nonempty(relative):
                errors.append('Delivery: output_files keys and paths must be nonempty strings');continue
            try:
                if Path(relative).is_absolute():raise ValueError('path must be workspace-relative')
                path=under(root,relative)
                if path.is_dir():raise ValueError('path must name a file, not a directory')
                if path in output_paths:raise ValueError('output paths must resolve to distinct files')
                output_paths.add(path)
            except (ValueError,OSError,RuntimeError) as exc:errors.append(f'Delivery: {kind}: {exc}')
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
    errors.extend(design_contract_errors(brief,style,template_snapshot=template_snapshot))
    errors.extend(visual_style_errors(style,slides))
    errors.extend(figure_framing_errors(root,assets,style))
    errors.extend(external_visual_errors(assets,sources,style))
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
        if visual.get('type') in {'original_figure','source_table','context_illustration'} and not visual.get('asset_ids'):
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
    coverage=data['design/slide_plan.json'].get('coverage',[])
    if not isinstance(coverage,list):errors.append('Coverage: must be a list')
    else:
        visibility={slide['id']:slide.get('hidden') for slide in slides if nonempty(slide.get('id'))}
        dispositions={'main':{False},'backup':{True},'main_and_backup':{False,True}}
        for n,item in enumerate(coverage,1):
            label=f'Coverage {n}'
            if not isinstance(item,dict):errors.append(f'{label}: must be an object');continue
            if not nonempty(item.get('topic')):errors.append(f'{label}: topic missing')
            disposition=item.get('disposition')
            if not isinstance(disposition,str) or disposition not in {*dispositions,'notes','excluded','source_gap'}:
                errors.append(f'{label}: invalid disposition');continue
            valid_slides=False
            for key,known in [('source_ids',source_ids),('slide_ids',slide_ids)]:
                refs=item.get(key)
                if not isinstance(refs,list) or any(not nonempty(ref) for ref in refs):
                    errors.append(f'{label}: {key} must be a list of nonempty IDs')
                elif len(set(refs))!=len(refs) or any(ref not in known for ref in refs):
                    errors.append(f'{label}: {key} contains duplicate or unknown IDs')
                elif key=='slide_ids':valid_slides=True
            if disposition in dispositions and valid_slides:
                actual={visibility[sid] for sid in item['slide_ids'] if type(visibility[sid]) is bool}
                if actual!=dispositions[disposition]:
                    errors.append(f'{label}: slide visibility does not match {disposition}')
            if disposition in {'excluded','source_gap'} and not nonempty(item.get('rationale')):
                errors.append(f'{label}: exclusions and source gaps require rationale')
    speaking_minutes=brief.get('target_minutes')
    if positive(speaking_minutes) and brief.get('qa_time_included') is True and positive(brief.get('qa_minutes')):
        speaking_minutes-=brief['qa_minutes']
    if positive(speaking_minutes) and abs(seconds-60*speaking_minutes)>max(60,speaking_minutes*6):
        errors.append('Visible-slide timing differs materially from the speaking budget (excluding reserved Q&A); revise plan or brief')
    return {'status':'fail' if errors else 'pass','errors':errors,'warnings':warnings,
            'planned_seconds':seconds,'slides':len(slides),'display_text_metrics':display_text_metrics,
            'meaning':'Metadata and provenance preflight; coverage checks references, not completeness. Display text metrics are informational, not density approval. Agent still judges evidence and design.'}


def preflight(args: argparse.Namespace) -> int:
    report=preflight_report(args.project.resolve());write(args.out,report)
    print(json.dumps(report,ensure_ascii=False,indent=2));return int(report['status']!='pass')


def snapshot_template(style: dict, dest: Path) -> dict:
    reference=style['template_reference'];source=Path(reference['root']).resolve()
    files=template_files(source,reference['spec']);package=dest/'template'
    fingerprints={}
    for relative,path in files.items():
        target=package/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target);fingerprints[relative]=sha256(target)
    path=package/'manifest.json'
    write(path,{'schema_version':1,'source_root':str(source),'spec':reference['spec'],'files':fingerprints})
    return {'source_root':str(source),'snapshot_root':'template','manifest':'template/manifest.json','sha256':sha256(path)}


def checked_template_snapshot(handoff_dir: Path, manifest: dict) -> tuple[dict, Path, dict]:
    """Verify the immutable package, never re-hash the mutable installation source."""
    record=manifest.get('template')
    if (not isinstance(record,dict) or record.get('snapshot_root')!='template'
            or record.get('manifest')!='template/manifest.json' or not nonempty(record.get('source_root'))):
        raise ValueError('Missing/incomplete template snapshot in handoff manifest')
    package=under(handoff_dir,record['snapshot_root']);path=under(handoff_dir,record['manifest'])
    if not path.is_file() or sha256(path)!=record.get('sha256'):
        raise ValueError('Missing/changed template snapshot manifest')
    data=load(path);files=data.get('files')
    if (data.get('schema_version')!=1 or data.get('source_root')!=record['source_root']
            or data.get('spec')!=BUILTIN_TEMPLATE_SPEC or not isinstance(files,dict)
            or data['spec'] not in files or not any(name.endswith('.svg') for name in files)):
        raise ValueError('Incomplete template snapshot file roster')
    actual={str(path.relative_to(package)) for path in package.rglob('*') if path.is_file() and path!=package/'manifest.json'}
    if actual!=set(files):raise ValueError('Template snapshot file roster differs from package')
    for relative,digest in files.items():
        path=under(package,relative)
        if not path.is_file() or sha256(path)!=digest:raise ValueError(f'Missing/changed template snapshot file: {relative}')
    return record,package,data


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
        if isinstance(item.get('context'),dict) and nonempty(item['context'].get('path')):
            context=item['context'];resources[context['path']]=sha256(under(root,context['path']))
    style=load(root/'design/style_profile.json')
    contract=style.get('design_contract',{})
    default_template=isinstance(contract,dict) and contract.get('mode')=='academic_navigator'
    manifest={'schema_version':'1','created_at':now(),'workspace':str(root),
              'preparation':fingerprints,'resources':resources}
    if default_template:manifest['template']=snapshot_template(style,dest)
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
    if 'design_contract' in style:
        text+='\n## Design mode and template decision\n\n```json\n'
        text+=json.dumps({'design_contract':style['design_contract'],
                         'template_reference':style.get('template_reference')},ensure_ascii=False,indent=2)+'\n```\n\n'
    if default_template:
        template_root=(dest/'template').resolve()
        text+=(f'Use the immutable Academic Navigator deck template rooted at `{template_root}`. '
               f'Its exact specification is `{template_root/BUILTIN_TEMPLATE_SPEC}` and its source manifest '
               f'is `{template_root/"manifest.json"}` (SHA-256 `{manifest["template"]["sha256"]}`). '
               'Pass this absolute root as an explicit template input at the backend template-choice stage; '
               'an ordinary generation request may default to free design. '
               'Select/apply this exact workspace through the current backend template-selection and installation route; '
               'do not treat it as optional style inspiration or replace it with free composition. '
               'Read its specification and SVG prototypes, adapt their layouts to the accepted section/page plan, '
               'and follow the current backend gates. Record the actual installed template root and its source-to-installed '
               'file mapping in template_application; installation provenance added to the specification is allowed. '
               'Selection in preparation is not proof of production application. The receipt and independent visual '
               'template_application review must both demonstrate application to the actual output.\n')
    if 'communication_contract' in style:
        text+='\n## Communication contract\n\n'
        text+='```json\n'+json.dumps(style['communication_contract'],ensure_ascii=False,indent=2)+'\n```\n\n'
        text+=('Apply every communication rule and the citation placement policy above. Independent review '
               'must check `audience_copy` against the planned display copy and `reference_match` against '
               'the supplied reference or recorded style basis; neither is approved by metadata or text counts.\n')
    visual_policy={key:style[key] for key in ['figure_policy','section_navigation','typography','palette_policy','page_chrome','content_grouping','external_visuals'] if key in style}
    layout=navigation_layout(style)
    if layout is not None:visual_policy['navigation_layout']=layout
    if visual_policy:
        text+='\n## Visual execution contract\n\n```json\n'+json.dumps(visual_policy,ensure_ascii=False,indent=2)+'\n```\n\n'
        text+=('For body_only/notes_only figures, use the display asset path on the slide. '
               'Keep its separate context image and caption_provenance for evidence review and speaker notes; '
               'do not place the long paper caption on the slide. Preserve scientific legends, axes, units and panel identifiers. '
               'When section navigation is enabled, preserve the ordered sections and derive the active tab from each slide section_id, '
               'respecting explicit exempt_slide_ids. For scope main_talk, list only sections used by visible non-exempt pages; '
               'hidden backups do not add navigation labels. Preserve the declared tab_gap_px at the canvas scale as visible space between tabs, '
               'rather than merging them into a compact bar. When navigation_layout is supplied, use its left-aligned group and equal tab coordinates; '
               'align with the title at x48, keep the same positions across pages and leave unused space on the right. Verify the actual label font fits without shrinking it. '
               'For active_indicator fill_only, use the filled active tab without an extra navigation underline; '
               'this does not remove the separate title separator. Preserve the declared font families and sizes for every typography role across slides, '
               'including the selected Latin and CJK faces in mixed-script font-family stacks; use the default Latin-first stack for previews, '
               'or record a documented equivalent backend script mapping and verify actual exported faces, textbox width and line breaks. '
               'Apply the declared accent color limit. '
               'When page_chrome is supplied, keep the identified covers to title and accepted metadata, move background explanation to content pages, '
               'apply its current-page-only number, bottom-right placement, background box and title-separator instructions. '
               'When content_grouping is enabled, organize multi-part prose with the accepted cards or numbered blocks instead of an undifferentiated text pile. '
               'Keep peer boxes consistent in dimensions and padding; distinct content roles may use a recorded different layout. '
               'Apply declared spacing at the canvas scale; retain clear gaps rather than stretching the last box to fill spare space. '
               'When external_visuals is enabled and the user has not limited sources, seek useful primary-source background or benchmark imagery. '
               'Register context_illustration assets with source_ids, exact source versions, source_locator and usage context_only. '
               'Attribute them on the slide or in its notes; never present their external results as evidence for the supplied work. '
               'Respect any explicit source-only restriction. Actual external assets require independent external_visual_provenance review. '
               'These are production instructions; metadata checks do not approve actual framing, typography, navigation, colors, cover content, grouping or provenance judgment.\n')
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
    if default_template:
        receipt['template_application']={'status':'pending',
            'handoff_template_sha256':manifest['template']['sha256'],'installed_template_root':'',
            'application_record':{'path':'','sha256':''}}
        write(dest/'template_application.example.json',{
            'handoff_template_sha256':manifest['template']['sha256'],'installed_template_root':'',
            'application_notes':'',
            'files':{relative:{'path':'','sha256':''} for relative in load(dest/'template/manifest.json')['files']}})
    else:receipt.pop('template_application',None)
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
    try:
        brief=load(handoff_dir/'brief.json');style=load(handoff_dir/'design/style_profile.json')
        contract=style.get('design_contract',{})
        required=('design_contract_version' in brief and isinstance(contract,dict)
                  and contract.get('mode')=='academic_navigator')
        if required or 'template' in manifest:
            record,_,_=checked_template_snapshot(handoff_dir,manifest)
            if record['source_root']!=style.get('template_reference',{}).get('root'):
                errors.append('Template snapshot differs from selected template root')
    except (ValueError,OSError,KeyError,TypeError) as exc:errors.append(f'Template contract: {exc}')
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


def installed_spec_matches(source: Path, installed: Path) -> bool:
    if source.read_bytes()==installed.read_bytes():return True
    # Current ppt-master adds exactly a blank line and an installation provenance
    # line after the H1. No other specification rewrite is silently permitted.
    try:
        expected=source.read_text(encoding='utf-8').splitlines()
        actual=installed.read_text(encoding='utf-8').splitlines()
    except UnicodeError:return False
    h1=next((n for n,line in enumerate(actual) if line.startswith('# ')),None)
    if h1 is None or len(actual)<=h1+2 or actual[h1+1]!='':return False
    if not re.fullmatch(r'> \*\*Installed from\*\*: `[^`]+` \((?:library|explicit)\)',actual[h1+2]):return False
    return actual[:h1+1]+actual[h1+3:]==expected


def template_application_errors(project: Path, handoff_dir: Path, receipt: dict) -> list[str]:
    style=load(handoff_dir/'design/style_profile.json');contract=style.get('design_contract',{})
    if not isinstance(contract,dict) or contract.get('mode')!='academic_navigator':return []
    try:
        manifest=load(handoff_dir/'manifest.json')
        template,package,source=checked_template_snapshot(handoff_dir,manifest)
        application=receipt.get('template_application')
        if not isinstance(application,dict) or application.get('status')!='applied':
            raise ValueError('applied template_application receipt is required')
        if application.get('handoff_template_sha256')!=template['sha256']:
            raise ValueError('receipt must identify this handoff template manifest')
        location=application.get('installed_template_root')
        if not nonempty(location) or not Path(location).is_absolute() or not Path(location).is_dir():
            raise ValueError('actual absolute installed_template_root is required')
        installed_root=Path(location).resolve();reference=application.get('application_record')
        if not installed_root.is_relative_to((project/'production').resolve()):
            raise ValueError('installed_template_root must be a real installation under this workspace production/')
        if not isinstance(reference,dict) or not nonempty(reference.get('path')):
            raise ValueError('application_record path and SHA-256 are required')
        if Path(reference['path']).is_absolute():raise ValueError('application_record path must be workspace-relative')
        record_path=under(project,reference['path'])
        if not record_path.is_file() or sha256(record_path)!=reference.get('sha256'):
            raise ValueError('application_record is missing or its bytes changed')
        record=load(record_path)
        if (record.get('handoff_template_sha256')!=template['sha256']
                or record.get('installed_template_root')!=location or not nonempty(record.get('application_notes'))):
            raise ValueError('application_record must identify the same template, installation root and actual application notes')
        files=record.get('files')
        if not isinstance(files,dict) or set(files)!=set(source['files']):
            raise ValueError('application_record must map every snapshot specification/SVG file')
        targets=set()
        for relative,item in files.items():
            if not isinstance(item,dict) or not nonempty(item.get('path')) or Path(item['path']).is_absolute():
                raise ValueError(f'invalid installed file mapping: {relative}')
            target=under(installed_root,item['path'])
            if target in targets:raise ValueError('installed file mapping must be one-to-one')
            targets.add(target)
            if not target.is_file() or sha256(target)!=item.get('sha256'):
                raise ValueError(f'missing/changed installed template file: {relative}')
            matches=(installed_spec_matches(under(package,relative),target) if relative==source['spec']
                     else sha256(target)==source['files'][relative])
            if not matches:raise ValueError(f'installed file does not correspond to the handoff template: {relative}')
    except (ValueError,OSError,KeyError,TypeError) as exc:return [f'Template application: {exc}']
    return []


def review_init(args: argparse.Namespace) -> int:
    root=args.project.resolve();handoff_dir=args.handoff.resolve()
    errors=contract_errors(root,handoff_dir)
    if errors:raise ValueError('; '.join(errors))
    plan=load(root/'design/slide_plan.json')['slides']
    checks=review_checks(load(root/'design/style_profile.json'),load(root/'analysis/figure_manifest.json')['figures'])
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
    template_snapshot=None
    try:
        manifest=load(args.handoff/'manifest.json')
        if 'template' in manifest:_,template_snapshot,_=checked_template_snapshot(args.handoff,manifest)
    except (ValueError,OSError,KeyError,TypeError):pass  # contract_errors already reports the invalid snapshot.
    prep=preflight_report(root,template_snapshot=template_snapshot)
    errors+=prep['errors']
    checks=review_checks(load(root/'design/style_profile.json'),load(root/'analysis/figure_manifest.json')['figures'])
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
    errors.extend(template_application_errors(root,args.handoff,receipt))
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
