"""Exercise the real initialized design route with synthetic source and artifacts."""
import contextlib
import copy
import io
import json
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from helpers import w, d, workspace, mock_review_fixture


class DefaultDesignTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        sink=contextlib.redirect_stdout(io.StringIO())
        sink.__enter__();self.addCleanup(sink.__exit__,None,None,None)
        self.project=workspace(Path(self.tmp.name),current_design=True)

    def style(self):return d.load(self.project/'design/style_profile.json')

    def write_style(self,style):d.write(self.project/'design/style_profile.json',style)

    def assert_preflight_fails(self,fragment):
        report=w.preflight_report(self.project)
        self.assertEqual(report['status'],'fail')
        self.assertTrue(any(fragment in error for error in report['errors']),report['errors'])

    def applied_fixture(self, *, provenance=True):
        """Fabricated installation and review for UNIT TESTS, never a real approval."""
        args=mock_review_fixture(self.project)
        receipt=d.load(args.receipt);handoff=d.load(args.handoff/'manifest.json')
        _,package,manifest=w.checked_template_snapshot(args.handoff,handoff)
        installed=self.project/'production/synthetic-installation'
        shutil.copytree(package,installed)
        spec=installed/manifest['spec']
        if provenance:
            lines=spec.read_text(encoding='utf-8').splitlines()
            h1=next(i for i,line in enumerate(lines) if line.startswith('# '))
            lines[h1+1:h1+1]=['',f'> **Installed from**: `{package}/` (explicit)']
            spec.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        record={
            'handoff_template_sha256':handoff['template']['sha256'],
            'installed_template_root':str(installed),
            'application_notes':'SYNTHETIC UNIT TEST ONLY: fabricated application of the cover and numbered prototypes.',
            'files':{name:{'path':name,'sha256':d.sha256(installed/name)} for name in manifest['files']}}
        path=self.project/'production/synthetic-template-application.json';d.write(path,record)
        receipt['template_application']={
            'status':'applied','handoff_template_sha256':handoff['template']['sha256'],
            'installed_template_root':str(installed),
            'application_record':{'path':str(path.relative_to(self.project)),'sha256':d.sha256(path)}}
        d.write(args.receipt,receipt)
        review=d.load(args.review)
        checks=w.review_checks(self.style())
        for row in review['slides']:row.update({check:'pass' for check in checks})
        d.write(args.review,review)
        return args,path,installed

    def refresh_record(self,args,path,record):
        d.write(path,record);receipt=d.load(args.receipt)
        receipt['template_application']['application_record']['sha256']=d.sha256(path)
        d.write(args.receipt,receipt)

    def test_current_fixture_retains_initialized_defaults(self):
        brief=d.load(self.project/'brief.json');style=self.style()
        self.assertEqual(brief['design_contract_version'],1)
        self.assertEqual(brief['design_mode'],'academic_navigator')
        self.assertIn('Academic Navigator deck template',brief['style_intent'])
        self.assertEqual(brief['intake_confirmation']['requirements']['design_mode'],'academic_navigator')
        self.assertEqual(style['design_contract'],{'version':1,'mode':'academic_navigator'})
        self.assertEqual(style['template_reference']['status'],'selected')
        self.assertIs(style['template_reference']['applied'],False)
        self.assertEqual(style['section_navigation']['scope'],'main_talk')
        self.assertEqual(style['section_navigation']['tab_gap_px'],16)
        self.assertEqual(style['section_navigation']['width_mode'],'content')
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_unplanned_navigation_blocks_handoff(self):
        style=self.style();style['section_navigation']['sections']=[];self.write_style(style)
        self.assert_preflight_fails('sections must be a nonempty ordered list')
        with self.assertRaisesRegex(ValueError,'Preparation not ready'):
            w.handoff(Namespace(project=self.project,run_id='unplanned'))
        self.assertFalse((self.project/'handoff/unplanned').exists())

    def test_real_init_leaves_main_navigation_planning_pending(self):
        project=Path(self.tmp.name)/'fresh'
        w.init(Namespace(project=project,source=[Path(self.tmp.name)/'synthetic_source.md'],
                         template=None,minutes=2,language='en',audience='researchers'))
        style=d.load(project/'design/style_profile.json')
        self.assertEqual(style['section_navigation']['sections'],[])
        self.assertEqual(style['section_navigation']['scope'],'main_talk')
        self.assertGreater(style['section_navigation']['tab_gap_px'],0)
        self.assertTrue(any('sections must be a nonempty ordered list' in error
                            for error in w.preflight_report(project)['errors']))
        with self.assertRaisesRegex(ValueError,'Preparation not ready'):
            w.handoff(Namespace(project=project,run_id='unplanned'))
        self.assertFalse((project/'handoff/unplanned').exists())

    def test_real_init_supplies_mixed_script_fonts_to_every_native_role(self):
        project=Path(self.tmp.name)/'fresh-fonts'
        w.init(Namespace(project=project,source=[Path(self.tmp.name)/'synthetic_source.md'],
                         template=None,minutes=2,language='zh-CN',audience='researchers'))
        typography=d.load(project/'design/style_profile.json')['typography']
        stack='Times New Roman, Microsoft YaHei'
        self.assertEqual(typography['font_family'],stack)
        self.assertEqual(typography['latin_font_family'],'Times New Roman')
        self.assertEqual(typography['cjk_font_family'],'Microsoft YaHei')
        self.assertEqual({name:role['font_family'] for name,role in typography['roles'].items()},
                         {name:stack for name in ['cover','title','body','annotation','footer','navigation']})
        self.assertEqual({name:role['font_size_px'] for name,role in typography['roles'].items()},
                         {'cover':56,'title':40,'body':32,'annotation':24,'footer':16,'navigation':18})

    def test_main_navigation_rejects_backup_only_or_exempt_only_sections(self):
        original=self.style();path=self.project/'design/slide_plan.json';plan=d.load(path)
        for name,index in [('backup',2),('cover',0)]:
            with self.subTest(name=name):
                style=copy.deepcopy(original);candidate=copy.deepcopy(plan)
                style['section_navigation']['sections'].append({'id':name,'label':name})
                candidate['slides'][index]['section_id']=name
                self.write_style(style);d.write(path,candidate)
                self.assert_preflight_fails(f"main_talk navigation section '{name}' has no visible non-exempt slide")

    def test_default_navigation_requires_explicit_main_scope_and_positive_gap(self):
        original=self.style()
        for field,value in [('scope',None),('scope','all_slides'),('tab_gap_px',None),
                            ('tab_gap_px',0),('tab_gap_px',-1),('tab_gap_px',True)]:
            with self.subTest(field=field,value=value):
                style=copy.deepcopy(original)
                if value is None:style['section_navigation'].pop(field)
                else:style['section_navigation'][field]=value
                self.write_style(style)
                self.assert_preflight_fails('scope main_talk and positive tab_gap_px')
        style=copy.deepcopy(original);style['section_navigation']['tab_gap_px']=8
        self.write_style(style)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_main_sections_allow_hidden_backups_without_a_navigation_label(self):
        path=self.project/'design/slide_plan.json';plan=d.load(path)
        plan['slides'][2].pop('section_id');d.write(path,plan)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        plan['slides'][2]['section_id']='example';d.write(path,plan)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        plan['slides'][2]['section_id']='backup-only';d.write(path,plan)
        self.assert_preflight_fails('P03: section_id must reference section_navigation sections')

    def test_main_navigation_accepts_multiple_visible_sections(self):
        style=self.style();style['section_navigation']['sections'].append({'id':'analysis','label':'Analysis'})
        self.write_style(style)
        path=self.project/'design/slide_plan.json';plan=d.load(path)
        plan['slides'][1]['seconds']=90
        plan['slides'][2].update(hidden=False,section_id='analysis',seconds=15)
        d.write(path,plan)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_content_navigation_left_aligns_two_compact_tabs(self):
        style=self.style()
        style['section_navigation']['sections']=[{'id':'background','label':'背景'},
                                                 {'id':'evidence','label':'证据'}]
        before=copy.deepcopy(style);layout=w.navigation_layout(style)
        self.assertEqual(style,before)
        self.assertEqual(layout['reference_canvas'],{'width':1280,'height':720})
        self.assertEqual(layout['group'],{'x':48,'y':20,'width':272,'height':44})
        self.assertEqual([tab['text'] for tab in layout['tabs']],['01 背景','02 证据'])
        self.assertEqual([tab['section_id'] for tab in layout['tabs']],['background','evidence'])
        for index,tab in enumerate(layout['tabs']):
            self.assertEqual((tab['x'],tab['y'],tab['width'],tab['height']),(48+index*144,20,128,44))
            self.assertEqual((tab['text_x'],tab['text_y']),(112+index*144,48))
        self.assertEqual(layout['font_size_px'],18)
        self.assertEqual(layout['padding_x_px'],24)

    def test_content_navigation_grows_with_longest_label_and_section_count(self):
        style=self.style();navigation=style['section_navigation']
        for count in [1,2,5]:
            navigation['sections']=[{'id':str(i),'label':'方法'} for i in range(count)]
            layout=w.navigation_layout(style);group=layout['group'];tabs=layout['tabs']
            self.assertEqual(group['width'],count*128+(count-1)*16)
            self.assertEqual(group['x'],48)
            self.assertLessEqual(group['x']+group['width'],1232)
            self.assertEqual([tab['x'] for tab in tabs],[48+i*144 for i in range(count)])
            for previous,current in zip(tabs,tabs[1:]):
                self.assertEqual(current['x']-previous['x']-previous['width'],16)
        navigation['sections']=[{'id':'a','label':'背景'},{'id':'b','label':'实验结果与对照分析'}]
        layout=w.navigation_layout(style)
        self.assertGreater(layout['tabs'][0]['width'],128)
        self.assertEqual(layout['tabs'][0]['width'],layout['tabs'][1]['width'])
        self.assertEqual(layout['tabs'][0]['width']%8,0)
        self.assertLess(layout['group']['width'],1184)

    def test_content_navigation_budgets_wide_letters_and_combining_marks(self):
        style=self.style();section=style['section_navigation']['sections'][0]
        section['label']='A'*12;plain=w.navigation_layout(style)['tabs'][0]['width']
        section['label']='A\u0301'*12;combined=w.navigation_layout(style)['tabs'][0]['width']
        section['label']='Ａ'*12;wide=w.navigation_layout(style)['tabs'][0]['width']
        self.assertEqual(plain,combined)
        self.assertGreater(wide,plain)

    def test_content_navigation_rejects_invalid_mode_and_overflow_before_handoff(self):
        original=self.style()
        for mode in [None,[],False,'stretch']:
            with self.subTest(mode=mode):
                style=copy.deepcopy(original);style['section_navigation']['width_mode']=mode
                self.write_style(style);self.assert_preflight_fails('width_mode must be content')
        for sections in [[{'id':'example','label':'长'*80}],
                         [{'id':str(i),'label':'短'} for i in range(9)]]:
            with self.subTest(sections=sections):
                style=copy.deepcopy(original);style['section_navigation']['sections']=sections
                self.write_style(style);self.assert_preflight_fails('content width exceeds 1184 px')
                with self.assertRaisesRegex(ValueError,'Preparation not ready'):
                    w.handoff(Namespace(project=self.project,run_id='overflow'))
                self.assertFalse((self.project/'handoff/overflow').exists())

    def test_content_navigation_handoff_contains_concrete_geometry(self):
        w.handoff(Namespace(project=self.project,run_id='content-navigation'))
        text=(self.project/'handoff/content-navigation/handoff.md').read_text(encoding='utf-8')
        contracts=[json.loads(block) for block in re.findall(r'```json\n(.*?)\n```',text,re.DOTALL)]
        visual=next(contract for contract in contracts if 'navigation_layout' in contract)
        self.assertEqual(visual['navigation_layout'],w.navigation_layout(self.style()))
        self.assertIn('align with the title at x48',text)
        self.assertIn('leave unused space on the right',text)

    def test_legacy_navigation_keeps_saved_geometry(self):
        style=self.style();style['section_navigation'].pop('width_mode');self.write_style(style)
        path=self.project/'design/style_profile.json';before=path.read_bytes()
        self.assertIsNone(w.navigation_layout(style))
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        w.handoff(Namespace(project=self.project,run_id='legacy-navigation'))
        self.assertEqual(path.read_bytes(),before)
        snapshot=self.project/'handoff/legacy-navigation/design/style_profile.json'
        self.assertEqual(snapshot.read_bytes(),before)
        text=(self.project/'handoff/legacy-navigation/handoff.md').read_text(encoding='utf-8')
        self.assertNotIn('"navigation_layout":',text)

    def test_template_selection_is_required_without_pretending_application(self):
        original=self.style()
        for patch_value in [{'status':'pending_default'},{'root':'/synthetic/missing-template'},
                            {'spec':'templates/nonexistent.md'},{'kind':'style-reference'}]:
            with self.subTest(patch=patch_value):
                style=copy.deepcopy(original);style['template_reference'].update(patch_value);self.write_style(style)
                self.assert_preflight_fails('Design contract:')
        self.write_style(original)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        self.assertIs(original['template_reference']['applied'],False)

    def test_new_brief_rejects_legacy_profile_and_removal_of_its_marker(self):
        self.write_style({'name':'legacy','basis':'Legacy synthetic fixture','review_status':'verified'})
        self.assert_preflight_fails('style requires version 1')
        path=self.project/'brief.json';brief=d.load(path);brief.pop('design_contract_version');d.write(path,brief)
        self.assert_preflight_fails('requirements changed')

    def test_design_mode_change_or_removal_invalidates_intake(self):
        path=self.project/'brief.json';original=d.load(path)
        for mode in ['user_override',None]:
            with self.subTest(mode=mode):
                brief=copy.deepcopy(original)
                if mode is None:brief.pop('design_mode')
                else:brief['design_mode']=mode
                d.write(path,brief)
                self.assert_preflight_fails('requirements changed')

    def test_design_mode_requires_version_before_confirmation(self):
        brief=d.load(self.project/'brief.json');brief.pop('design_contract_version')
        brief['intake_confirmation']={'status':'pending','user_response':'','requirements':{}}
        errors=w.design_contract_errors(brief,self.style())
        self.assertTrue(any('design_contract_version' in error for error in errors),errors)

    def test_older_v1_brief_without_design_mode_remains_accepted(self):
        path=self.project/'brief.json';brief=d.load(path);brief.pop('design_mode')
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief)
        d.write(path,brief);before=path.read_bytes()
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        w.intake(Namespace(project=self.project))
        w.handoff(Namespace(project=self.project,run_id='older-v1'))
        self.assertEqual(path.read_bytes(),before)
        self.assertNotIn('design_mode',d.load(self.project/'handoff/older-v1/brief.json'))

    def test_default_policies_cannot_be_deleted(self):
        original=self.style()
        for key in ['design_contract','communication_contract','figure_policy','section_navigation','typography',
                    'palette_policy','page_chrome','content_grouping','external_visuals','template_reference']:
            with self.subTest(key=key):
                style=copy.deepcopy(original);style.pop(key);self.write_style(style)
                self.assert_preflight_fails('Design contract:')

    def test_default_policies_cannot_be_disabled_or_weakened(self):
        original=self.style()
        changes=[('section_navigation',{'enabled':False}),
                 ('page_chrome',{'title_separator':{'enabled':False}}),
                 ('page_chrome',{'page_number':{'format':'current','position':'bottom_right','background':False}}),
                 ('content_grouping',{'enabled':False}),('content_grouping',{'same_role_consistency':False}),
                 ('content_grouping',{'spacing':{'min_gap_px':0,'padding_px':20}}),
                 ('palette_policy',{'max_accent_colors':3,'accent_colors':['#2F5597','#FF0000']}),
                 ('typography',{'roles':{'title':{'font_family':'Synthetic','font_size_px':40}}})]
        for key,change in changes:
            with self.subTest(key=key,change=change):
                style=copy.deepcopy(original);style[key].update(change);self.write_style(style)
                self.assert_preflight_fails('Design contract:')

    def test_source_only_can_explicitly_disable_external_images(self):
        style=self.style();style['external_visuals']={'enabled':False};self.write_style(style)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_default_policies_allow_extra_nonconflicting_geometry_and_provenance(self):
        style=self.style()
        style['page_chrome']['page_number']['geometry']={'x':1164,'y':674,'width':68,'height':36}
        style['figure_policy']['basis']='Synthetic provenance annotation; body-only policy is unchanged.'
        self.write_style(style)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_explicit_user_override_allows_different_style_and_no_template(self):
        path=self.project/'brief.json';brief=d.load(path)
        instruction='SYNTHETIC USER INSTRUCTION: use plain white slides without navigation or a template.'
        brief['style_intent']=instruction;brief['intake_confirmation']['user_response']=instruction
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief);d.write(path,brief)
        style={'name':'synthetic-user-override','basis':instruction,'review_status':'verified',
               'design_contract':{'version':1,'mode':'user_override',
                                  'override':{'reason':'Explicit synthetic request for a different style.',
                                              'user_instruction':instruction}}}
        self.write_style(style)
        self.assert_preflight_fails('design_mode')
        brief['design_mode']='user_override'
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief);d.write(path,brief)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        args=mock_review_fixture(self.project)
        self.assertEqual(w.gate(args),0)
        self.assertNotIn('template',d.load(args.handoff/'manifest.json'))
        style['design_contract']['override']['user_instruction']='Backend chose its own free layout.'
        self.write_style(style);self.assert_preflight_fails('instruction must be quoted')

    def test_pending_supplied_template_override_does_not_infer_user_choice(self):
        project=Path(self.tmp.name)/'supplied-template';reference=Path(self.tmp.name)/'reference.svg'
        reference.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        w.init(Namespace(project=project,source=[Path(self.tmp.name)/'synthetic_source.md'],
                         template=reference,minutes=2,language='en',audience='researchers'))
        brief=d.load(project/'brief.json');style=d.load(project/'design/style_profile.json')
        self.assertEqual(brief['design_mode'],'user_override')
        self.assertEqual(brief['style_intent'],'')
        self.assertEqual(brief['intake_confirmation']['status'],'pending')
        self.assertNotIn('template_reference',style)
        self.assertEqual(style['design_contract']['mode'],'user_override')
        errors=w.design_contract_errors(brief,style)
        self.assertTrue(any('actual user_instruction' in error for error in errors))

    def test_handoff_pins_actual_package_and_requires_backend_application(self):
        w.handoff(Namespace(project=self.project,run_id='pinned'))
        handoff=self.project/'handoff/pinned';manifest=d.load(handoff/'manifest.json')
        record,package,data=w.checked_template_snapshot(handoff,manifest)
        self.assertEqual(record['source_root'],str(w.BUILTIN_TEMPLATE_ROOT.resolve()))
        self.assertEqual(len(data['files']),5)
        for name,digest in data['files'].items():
            self.assertEqual(d.sha256(package/name),digest)
            self.assertEqual(d.sha256(w.BUILTIN_TEMPLATE_ROOT/name),digest)
        text=(handoff/'handoff.md').read_text()
        typography=self.style()['typography']
        self.assertEqual(d.load(handoff/'design/style_profile.json')['typography'],typography)
        blocks=[json.loads(block) for block in re.findall(r'```json\n(.*?)\n```',text,re.S)]
        self.assertEqual(next(block['typography'] for block in blocks if 'typography' in block),typography)
        prototypes=[name for name in data['files'] if name.endswith('.svg')]
        self.assertEqual(len(prototypes),4)
        for name in prototypes:
            root=ET.parse(package/name).getroot()
            self.assertEqual(root.get('font-family'),'Times New Roman, Microsoft YaHei')
        self.assertIn(str(package),text)
        self.assertIn('do not treat it as optional style inspiration',text)
        self.assertIn('"status": "selected"',text)
        pending=d.load(handoff/'build_receipt.template.json')['template_application']
        self.assertEqual(pending['status'],'pending')
        self.assertEqual(pending['handoff_template_sha256'],record['sha256'])
        self.assertEqual(set(d.load(handoff/'template_application.example.json')['files']),set(data['files']))
        self.assertEqual(w.contract_errors(self.project,handoff),[])

    def test_handoff_preserves_accepted_font_override(self):
        instruction='SYNTHETIC USER INSTRUCTION: use Fixture Latin Serif and Fixture CJK Sans.'
        brief=d.load(self.project/'brief.json');brief['style_intent']=instruction
        brief['intake_confirmation']['user_response']=instruction
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief)
        d.write(self.project/'brief.json',brief)
        style=self.style();typography=style['typography']
        typography.update(font_family='Fixture Latin Serif, Fixture CJK Sans',
                          latin_font_family='Fixture Latin Serif',cjk_font_family='Fixture CJK Sans')
        for role in typography['roles'].values():role['font_family']=typography['font_family']
        self.write_style(style)
        w.handoff(Namespace(project=self.project,run_id='font-override'))
        handoff=self.project/'handoff/font-override'
        self.assertEqual(d.load(handoff/'design/style_profile.json')['typography'],typography)
        self.assertEqual(self.style()['typography'],typography)

    def test_snapshot_file_loss_or_tampering_invalidates_contract(self):
        w.handoff(Namespace(project=self.project,run_id='snapshot'))
        handoff=self.project/'handoff/snapshot';spec=handoff/'template'/w.BUILTIN_TEMPLATE_SPEC
        original=spec.read_bytes();spec.write_bytes(original+b'\nChanged synthetic specification.\n')
        self.assertTrue(any('changed template snapshot file' in error for error in w.contract_errors(self.project,handoff)))
        spec.write_bytes(original);(handoff/'template/templates/01_cover.svg').unlink()
        self.assertTrue(w.contract_errors(self.project,handoff))

    def test_fresh_default_route_needs_application_receipt_and_visual_review(self):
        args=mock_review_fixture(self.project)
        review=d.load(args.review)
        self.assertTrue(all(row['template_application']=='pending' for row in review['slides']))
        self.assertTrue(all(row['projection_readability']=='pending' for row in review['slides']))
        for row in review['slides']:row.update({key:'pass' for key in w.review_checks(self.style())})
        d.write(args.review,review)
        self.assertEqual(w.gate(args),1)
        self.assertTrue(any('applied template_application' in error for error in d.load(args.out)['errors']))
        receipt=d.load(args.receipt);receipt['template_application']={'status':'applied'};d.write(args.receipt,receipt)
        self.assertEqual(w.gate(args),1)
        self.assertTrue(any('this handoff template' in error for error in d.load(args.out)['errors']))

    def test_valid_current_route_accepts_standard_backend_installation_provenance(self):
        args,path,installed=self.applied_fixture()
        self.assertEqual(w.gate(args),0)
        review=d.load(args.review);review['slides'][1]['template_application']='pending';d.write(args.review,review)
        self.assertEqual(w.gate(args),1)
        self.assertIn('Slide 2: template_application not passed',d.load(args.out)['errors'])

    def test_projection_readability_requires_explicit_final_page_review(self):
        args,_,_=self.applied_fixture()
        approved=d.load(args.review)
        for state in [None,'pending','fail']:
            with self.subTest(state=state):
                review=copy.deepcopy(approved)
                if state is None:review['slides'][1].pop('projection_readability')
                else:review['slides'][1]['projection_readability']=state
                d.write(args.review,review)
                self.assertEqual(w.gate(args),1)
                self.assertIn('Slide 2: projection_readability not passed',d.load(args.out)['errors'])
        d.write(args.review,approved)
        self.assertEqual(w.gate(args),0)

    def test_projection_readability_keeps_legacy_and_user_override_contracts(self):
        legacy_root=Path(self.tmp.name)/'legacy';legacy_root.mkdir()
        legacy=workspace(legacy_root)
        args=mock_review_fixture(legacy)
        self.assertNotIn('projection_readability',d.load(args.review)['slides'][0])
        self.assertEqual(w.gate(args),0)
        self.assertNotIn('projection_readability',w.review_checks({
            'design_contract':{'version':1,'mode':'user_override'}}))

    def test_gate_uses_snapshot_instead_of_mutable_skill_template_files(self):
        args,_,_=self.applied_fixture(provenance=False)
        original=w.template_files
        def snapshot_only(root,spec):
            self.assertNotEqual(root.resolve(),w.BUILTIN_TEMPLATE_ROOT.resolve())
            return original(root,spec)
        with patch.object(w,'template_files',side_effect=snapshot_only):
            self.assertEqual(w.gate(args),0)

    def test_mapping_allows_backend_rename_but_not_arbitrary_spec_changes(self):
        args,path,installed=self.applied_fixture()
        record=d.load(path);spec=record['files'][w.BUILTIN_TEMPLATE_SPEC]
        renamed=installed/'templates/renamed-design-spec.md'
        (installed/spec['path']).rename(renamed);spec['path']=str(renamed.relative_to(installed))
        self.refresh_record(args,path,record);self.assertEqual(w.gate(args),0)
        renamed.write_text(renamed.read_text()+'\nUse an unrelated synthetic visual style.\n')
        spec['sha256']=d.sha256(renamed);self.refresh_record(args,path,record)
        self.assertEqual(w.gate(args),1)
        self.assertTrue(any('does not correspond' in error for error in d.load(args.out)['errors']))

    def test_receipt_cannot_substitute_unrelated_files_or_skip_mapping(self):
        args,path,installed=self.applied_fixture();original=d.load(path)
        for change in ['missing map','different source','outside file','missing file','blank notes']:
            with self.subTest(change=change):
                record=copy.deepcopy(original)
                if change=='missing map':record['files'].pop('templates/01_cover.svg')
                elif change=='different source':record['handoff_template_sha256']='wrong'
                elif change=='outside file':record['files']['templates/01_cover.svg']['path']='../../outside.svg'
                elif change=='missing file':record['files']['templates/01_cover.svg']['path']='missing.svg'
                else:record['application_notes']=' '
                self.refresh_record(args,path,record);self.assertEqual(w.gate(args),1)
        self.refresh_record(args,path,original)
        image=installed/'templates/01_cover.svg';image.write_text('<svg>Synthetic unrelated replacement</svg>')
        original['files']['templates/01_cover.svg']['sha256']=d.sha256(image)
        self.refresh_record(args,path,original);self.assertEqual(w.gate(args),1)

    def test_snapshot_or_skill_root_is_not_an_actual_backend_installation(self):
        args,_,_=self.applied_fixture();receipt=d.load(args.receipt)
        for location in [str(args.handoff/'template'),str(w.BUILTIN_TEMPLATE_ROOT)]:
            with self.subTest(location=location):
                receipt['template_application']['installed_template_root']=location;d.write(args.receipt,receipt)
                self.assertEqual(w.gate(args),1)
                self.assertTrue(any('real installation under' in error for error in d.load(args.out)['errors']))


if __name__=='__main__':unittest.main()
