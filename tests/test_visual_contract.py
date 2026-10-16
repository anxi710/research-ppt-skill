"""Synthetic framing, navigation and presentation-style contract regressions."""
import contextlib
import copy
import io
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from helpers import w, d, workspace, mock_review_fixture


class VisualContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.redirect=contextlib.redirect_stdout(io.StringIO())
        self.redirect.__enter__();self.addCleanup(self.redirect.__exit__,None,None,None)
        self.project=workspace(Path(self.tmp.name))

    def enable_visual_policy(self):
        path=self.project/'design/style_profile.json';style=d.load(path)
        style.update(
            communication_contract={'version':1,'citation_placement':'notes',
                                    'rules':['Synthetic examples must remain labelled as synthetic.']},
            figure_policy={'display_region':'body_only','caption_policy':'notes_only'},
            section_navigation={'enabled':True,'sections':[{'id':'setup','label':'背景'},
                                                          {'id':'method','label':'方法'}]},
            typography={'roles':{name:{'font_family':'Synthetic Fixture Sans','font_size_px':size}
                                 for name,size in [('title',40),('body',28),('annotation',22),
                                                   ('footer',14),('navigation',20)]}},
            palette_policy={'accent_colors':['#126A70'],'max_accent_colors':1})
        d.write(path,style)
        path=self.project/'design/slide_plan.json';plan=d.load(path)
        for slide in plan['slides']:
            slide.update(display_title='合成示例',section_id='method')
        d.write(path,plan)
        return style,plan

    def add_figure(self):
        from PIL import Image
        paths=[]
        for name,color in [('body.png','white'),('context.png','gray')]:
            path=self.project/'assets/paper'/name;Image.new('RGB',(40,20),color).save(path);paths.append(path)
        asset={'id':'F1','kind':'original_figure','source_id':'S1','evidence_ids':['C1'],
               'path':str(paths[0].relative_to(self.project)),'sha256':d.sha256(paths[0]),
               'pdf_page':1,'bbox_pt':[20,20,280,100],
               'context':{'path':str(paths[1].relative_to(self.project)),'sha256':d.sha256(paths[1]),
                          'pdf_page':1,'bbox_pt':[0,0,300,200]},
               'caption_provenance':{'text':'图1：仅用于测试的合成示例。','locator':'合成来源，第1页，图1'},
               'review_status':'verified'}
        d.write(self.project/'analysis/figure_manifest.json',{'figures':[asset]})
        return asset

    def enable_page_policy(self):
        path=self.project/'design/style_profile.json';style=d.load(path)
        style.update(page_chrome={
            'cover':{'slide_ids':['P01'],'title_information_only':True},
            'page_number':{'format':'current','position':'bottom_right','background':True},
            'title_separator':{'enabled':True}},
            content_grouping={'enabled':True,'treatments':['cards','numbered_blocks']})
        d.write(path,style)
        return style

    def add_context_visual(self):
        asset=self.add_figure()
        for key in ['source_id','context','caption_provenance','pdf_page','bbox_pt']:
            asset.pop(key)
        asset.update(kind='context_illustration',source_ids=['S1'],
                     source_locator='Synthetic source v1, task-interface teaching panel',
                     purpose='benchmark_context',usage='context_only',evidence_ids=[])
        d.write(self.project/'analysis/figure_manifest.json',{'figures':[asset]})
        path=self.project/'design/slide_plan.json';plan=d.load(path)
        plan['slides'][0]['primary_visual'].update(type='context_illustration',asset_ids=['F1'])
        d.write(path,plan)
        return asset

    def test_legacy_workspace_keeps_existing_review_contract(self):
        # Earlier manifests did not separate a display crop and caption context.
        asset=self.add_figure();asset.pop('context');asset.pop('caption_provenance')
        d.write(self.project/'analysis/figure_manifest.json',{'figures':[asset]})
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        self.assertEqual(w.review_checks(d.load(self.project/'design/style_profile.json')),w.CHECKS)
        args=mock_review_fixture(self.project)
        self.assertEqual(w.gate(args),0)

    def test_asset_only_framing_opt_in_also_adds_review_check(self):
        asset=self.add_figure();asset.update(display_region='body_only',caption_policy='notes_only')
        d.write(self.project/'analysis/figure_manifest.json',{'figures':[asset]})
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        args=mock_review_fixture(self.project)
        self.assertEqual(d.load(args.review)['slides'][0]['figure_framing'],'pending')
        self.assertEqual(w.gate(args),1)
        self.assertIn('Slide 1: figure_framing not passed',d.load(args.out)['errors'])

    def test_navigation_uses_section_ids_and_requires_valid_mapping(self):
        style,plan=self.enable_visual_policy()
        # The old human-readable planning label is not a stable navigation key.
        plan['slides'][0]['section']='A stale planning label'
        path=self.project/'design/slide_plan.json';d.write(path,plan)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        for index,value in [(0,None),(0,'unknown'),(1,'unknown')]:
            with self.subTest(index=index,value=value):
                invalid=copy.deepcopy(plan)
                if value is None:invalid['slides'][index].pop('section_id')
                else:invalid['slides'][index]['section_id']=value
                d.write(path,invalid)
                self.assertIn(f'P0{index+1}: section_id must reference section_navigation sections',
                              w.preflight_report(self.project)['errors'])
        # A hidden backup can omit navigation, while a visible exception is explicit.
        plan['slides'][1].pop('section_id');plan['slides'][0].pop('section_id')
        style['section_navigation']['exempt_slide_ids']=['P01']
        d.write(path,plan);d.write(self.project/'design/style_profile.json',style)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_navigation_rejects_ambiguous_sections_and_unknown_exemptions(self):
        original,_=self.enable_visual_policy()
        for patch in [{'enabled':'yes'},{'sections':[]},
                      {'sections':[{'id':'method','label':'方法'},{'id':'method','label':'实验'}]},
                      {'sections':[{'id':'method','label':' '}]},
                      {'exempt_slide_ids':['P99']},
                      {'active_indicator':'fill_and_underline'},{'active_indicator':[]}]:
            with self.subTest(patch=patch):
                style=copy.deepcopy(original);style['section_navigation'].update(patch)
                d.write(self.project/'design/style_profile.json',style)
                self.assertEqual(w.preflight_report(self.project)['status'],'fail')

    def test_body_crop_requires_separate_verifiable_context_and_caption(self):
        self.enable_visual_policy();asset=self.add_figure()
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        cases=[('context absent',lambda a:a.pop('context')),
               ('caption absent',lambda a:a.pop('caption_provenance')),
               ('context bytes changed',lambda a:a['context'].update(sha256='wrong')),
               ('outside context',lambda a:a['context'].update(bbox_pt=[30,0,300,200])),
               ('negative context',lambda a:a['context'].update(bbox_pt=[-1,0,300,200])),
               ('page mismatch',lambda a:a['context'].update(pdf_page=2)),
               ('escape path',lambda a:a['context'].update(path='../outside.png')),
               ('display reused',lambda a:a['context'].update(path=a['path'],sha256=a['sha256']))]
        for name,mutate in cases:
            with self.subTest(case=name):
                invalid=copy.deepcopy(asset);mutate(invalid)
                d.write(self.project/'analysis/figure_manifest.json',{'figures':[invalid]})
                self.assertEqual(w.preflight_report(self.project)['status'],'fail')

    def test_standalone_png_keeps_context_without_fabricated_pdf_coordinates(self):
        self.enable_visual_policy();asset=self.add_figure()
        for record in [asset,asset['context']]:
            record.pop('pdf_page');record.pop('bbox_pt')
        asset['caption_provenance']['locator']='Synthetic standalone PNG source, figure caption'
        brief=d.load(self.project/'brief.json')
        brief['sources'][0].update(path=asset['context']['path'],sha256=asset['context']['sha256'],
                                  original_name='synthetic-source.png',version='synthetic PNG fixture v1')
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief)
        d.write(self.project/'brief.json',brief)
        path=self.project/'analysis/figure_manifest.json';d.write(path,{'figures':[asset]})
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        for name,mutate in [('context absent',lambda a:a.pop('context')),
                            ('context missing file',lambda a:a['context'].update(path='missing.png')),
                            ('context fingerprint wrong',lambda a:a['context'].update(sha256='wrong')),
                            ('caption provenance absent',lambda a:a.pop('caption_provenance'))]:
            with self.subTest(case=name):
                invalid=copy.deepcopy(asset);mutate(invalid);d.write(path,{'figures':[invalid]})
                self.assertEqual(w.preflight_report(self.project)['status'],'fail')

    def test_partial_pdf_coordinates_on_either_side_require_complete_pair(self):
        self.enable_visual_policy();original=self.add_figure()
        for record in [original,original['context']]:
            record.pop('pdf_page');record.pop('bbox_pt')
        for side in ['display','context']:
            for field,value in [('pdf_page',1),('bbox_pt',[0,0,300,200])]:
                with self.subTest(side=side,field=field):
                    asset=copy.deepcopy(original)
                    target=asset if side=='display' else asset['context'];target[field]=value
                    d.write(self.project/'analysis/figure_manifest.json',{'figures':[asset]})
                    self.assertEqual(w.preflight_report(self.project)['status'],'fail')

    def test_visual_roles_and_accent_limit_require_concrete_values(self):
        original,_=self.enable_visual_policy()
        for field,value in [('font_family',' '),('font_size_px',True),('font_size_px',0)]:
            with self.subTest(field=field,value=value):
                style=copy.deepcopy(original);style['typography']['roles']['body'][field]=value
                d.write(self.project/'design/style_profile.json',style)
                self.assertTrue(any('typography role body' in e for e in w.preflight_report(self.project)['errors']))
        style=copy.deepcopy(original);style['palette_policy']['accent_colors']=['#126A70','#EE3300']
        d.write(self.project/'design/style_profile.json',style)
        self.assertIn('Style: palette_policy accent colors exceed the declared limit',w.preflight_report(self.project)['errors'])

    def test_review_seeds_visual_checks_and_gate_rejects_pending_checks(self):
        self.enable_visual_policy();args=mock_review_fixture(self.project)
        target=self.project/'qa/fresh-review.json'
        w.review_init(Namespace(project=self.project,pptx=args.pptx,handoff=args.handoff,
                                render_report=args.render_report,out=target))
        visual=['figure_framing','section_navigation','typography_consistency','palette_consistency']
        for row in d.load(target)['slides']:
            self.assertTrue(all(row[check]=='pending' for check in visual))
        review=d.load(args.review)
        for row in review['slides']:row.update(audience_copy='pass',reference_match='pass')
        d.write(args.review,review)
        self.assertEqual(w.gate(args),1)
        for check in visual:self.assertIn(f'Slide 1: {check} not passed',d.load(args.out)['errors'])
        # Only a separately recorded review can satisfy the additional checks.
        for row in review['slides']:row.update({check:'pass' for check in visual})
        d.write(args.review,review);self.assertEqual(w.gate(args),0)

    def test_handoff_fingerprints_context_as_well_as_display_asset(self):
        self.enable_visual_policy();asset=self.add_figure()
        w.handoff(Namespace(project=self.project,run_id='framing'))
        handoff=self.project/'handoff/framing';manifest=d.load(handoff/'manifest.json')
        self.assertEqual(manifest['resources'][asset['context']['path']],asset['context']['sha256'])
        text=(handoff/'handoff.md').read_text()
        self.assertIn('derive the active tab from each slide section_id',text)
        self.assertIn('Preserve scientific legends, axes, units and panel identifiers',text)
        (self.project/asset['context']['path']).write_bytes(b'Changed synthetic context')
        self.assertIn(f'Changed source/asset: {asset["context"]["path"]}',w.contract_errors(self.project,handoff))

    def test_page_policies_require_independent_review_even_when_configuration_is_valid(self):
        style=self.enable_page_policy()
        # A valid cover policy says nothing about the actual cover's scientific content.
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        args=mock_review_fixture(self.project)
        review=d.load(args.review)
        for row in review['slides']:
            self.assertEqual(row['page_chrome'],'pending')
            self.assertEqual(row['content_grouping'],'pending')
        self.assertEqual(w.gate(args),1)
        errors=d.load(args.out)['errors']
        self.assertIn('Slide 1: page_chrome not passed',errors)
        self.assertIn('Slide 1: content_grouping not passed',errors)
        for row in review['slides']:row.update(page_chrome='pass',content_grouping='pass')
        d.write(args.review,review);self.assertEqual(w.gate(args),0)
        snapshot=d.load(args.handoff/'design/style_profile.json')
        self.assertEqual(snapshot['page_chrome'],style['page_chrome'])
        self.assertEqual(snapshot['content_grouping'],style['content_grouping'])

    def test_page_chrome_rejects_ambiguous_cover_and_malformed_chrome(self):
        original=self.enable_page_policy();path=self.project/'design/style_profile.json'
        cases=[None,{},
               {'cover':{'slide_ids':['P99'],'title_information_only':True}},
               {'cover':{'slide_ids':['P02'],'title_information_only':True}},
               {'cover':{'slide_ids':['P01','P01'],'title_information_only':True}},
               {'cover':{'slide_ids':[],'title_information_only':True}},
               {'cover':{'slide_ids':['P01'],'title_information_only':'yes'}},
               {'page_number':{'format':'current_total','position':'bottom_right','background':True}},
               {'page_number':{'format':'current','position':'top_left','background':True}},
               {'page_number':{'format':'current','position':'bottom_right','background':'box'}},
               {'title_separator':{'enabled':1}}]
        for chrome in cases:
            with self.subTest(chrome=chrome):
                style=copy.deepcopy(original);style['page_chrome']=chrome;d.write(path,style)
                self.assertTrue(any('page_chrome' in e for e in w.preflight_report(self.project)['errors']))
        # Cover, footer and separator can be adopted independently by a later project.
        for key in original['page_chrome']:
            with self.subTest(only=key):
                style=copy.deepcopy(original);style['page_chrome']={key:style['page_chrome'][key]};d.write(path,style)
                self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_grouping_is_optional_but_enabled_policy_needs_supported_treatments(self):
        original=self.enable_page_policy();path=self.project/'design/style_profile.json'
        for grouping in [None,{'enabled':'true'},{'enabled':True,'treatments':[]},
                         {'enabled':True,'treatments':['cards','cards']},
                         {'enabled':True,'treatments':['unstructured_prose']},
                         {'enabled':False,'same_role_consistency':'yes'},
                         {'enabled':True,'treatments':['cards'],'spacing':{'min_gap_px':0,'padding_px':20}},
                         {'enabled':True,'treatments':['cards'],'spacing':{'min_gap_px':24,'padding_px':True}}]:
            with self.subTest(grouping=grouping):
                style=copy.deepcopy(original);style['content_grouping']=grouping;d.write(path,style)
                self.assertTrue(any('content_grouping' in e for e in w.preflight_report(self.project)['errors']))
        for grouping in [{'enabled':False},{'enabled':True,'treatments':['cards']},
                         {'enabled':True,'treatments':['cards'],'same_role_consistency':True,
                          'spacing':{'min_gap_px':24,'padding_px':20}}]:
            with self.subTest(grouping=grouping):
                style=copy.deepcopy(original);style['content_grouping']=grouping;d.write(path,style)
                self.assertEqual(w.preflight_report(self.project)['status'],'pass')
                self.assertEqual('content_grouping' in w.review_checks(style),grouping['enabled'])

    def test_new_workspace_inherits_baseline_without_fabricating_section_plan_or_review(self):
        legacy=self.project/'design/style_profile.json';before=legacy.read_bytes()
        project=Path(self.tmp.name)/'new-default-talk'
        w.init(Namespace(project=project,source=[Path(self.tmp.name)/'synthetic_source.md'],
                         template=None,minutes=2,language='en',audience='researchers'))
        style=d.load(project/'design/style_profile.json')
        self.assertEqual(style['name'],'academic-navigator')
        self.assertEqual(style['page_chrome'],{
            'cover':{'slide_ids':['P01'],'title_information_only':True},
            'page_number':{'format':'current','position':'bottom_right','background':True},
            'title_separator':{'enabled':True}})
        self.assertEqual(style['content_grouping'],{
            'enabled':True,'treatments':['cards','numbered_blocks'],
            'same_role_consistency':True,'spacing':{'min_gap_px':24,'padding_px':20}})
        self.assertEqual(style['figure_policy'],{'display_region':'body_only','caption_policy':'notes_only'})
        self.assertEqual(style['palette_policy']['max_accent_colors'],1)
        self.assertIn('body',style['typography']['roles'])
        self.assertEqual(style['section_navigation'],{'enabled':True,'sections':[],
                                                      'exempt_slide_ids':['P01'],'active_indicator':'fill_only',
                                                      'scope':'main_talk','tab_gap_px':16})
        self.assertEqual(style['design_contract'],{'version':1,'mode':'academic_navigator'})
        self.assertEqual(d.load(project/'brief.json')['design_contract_version'],1)
        self.assertEqual(style['external_visuals'],{
            'enabled':True,'purposes':['background','benchmark_context'],
            'claim_boundary':'context_only','source_scope_precedence':True})
        self.assertNotIn('external_visual_provenance',w.review_checks(style))
        self.assertEqual(d.load(project/'design/slide_plan.json')['slides'],[])
        self.assertEqual(style['review_status'],'pending')
        self.assertEqual(d.load(project/'brief.json')['intake_confirmation']['status'],'pending')
        reference=style['template_reference']
        self.assertEqual(Path(reference['root']),Path(w.__file__).resolve().parents[1]/'assets/academic-navigator')
        self.assertTrue((Path(reference['root'])/reference['spec']).is_file())
        self.assertEqual(reference['kind'],'deck')
        self.assertEqual(reference['status'],'pending_default')
        self.assertIs(reference['applied'],False)
        # A supplied reference must not be recorded as choosing the built-in root.
        supplied=Path(self.tmp.name)/'synthetic-reference.svg'
        supplied.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"/>')
        explicit=Path(self.tmp.name)/'explicit-template-talk'
        w.init(Namespace(project=explicit,source=[Path(self.tmp.name)/'synthetic_source.md'],
                         template=supplied,minutes=2,language='en',audience='researchers'))
        explicit_style=d.load(explicit/'design/style_profile.json')
        self.assertNotIn('template_reference',explicit_style)
        self.assertEqual(explicit_style['design_contract'],{
            'version':1,'mode':'user_override','override':{'reason':'','user_instruction':''}})
        # Creating a new talk must not silently migrate a legacy talk's style.
        self.assertEqual(legacy.read_bytes(),before)
        with self.assertRaisesRegex(ValueError,'new/empty'):
            w.init(Namespace(project=self.project,source=[Path(self.tmp.name)/'synthetic_source.md'],
                             template=None,minutes=2,language='en',audience='researchers'))
        self.assertEqual(legacy.read_bytes(),before)

    def test_external_context_requires_traceable_sources_and_context_boundary(self):
        asset=self.add_context_visual();path=self.project/'analysis/figure_manifest.json'
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        for patch in [{'source_ids':[]},{'source_ids':['UNKNOWN']},{'source_ids':['S1','S1']},
                      {'source_locator':''},{'usage':'research_result'},{'purpose':'decoration'},
                      {'purpose':[]},{'sha256':'changed'}]:
            with self.subTest(patch=patch):
                invalid=dict(asset,**patch);d.write(path,{'figures':[invalid]})
                self.assertEqual(w.preflight_report(self.project)['status'],'fail')
        d.write(path,{'figures':[asset]})
        brief=d.load(self.project/'brief.json');brief['sources'][0]['version']=''
        d.write(self.project/'brief.json',brief)
        self.assertIn('Source S1: exact version not recorded',w.preflight_report(self.project)['errors'])
        # A style reference's version exemption cannot stand in for content provenance.
        brief['sources'][0]['role']='style_reference'
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief)
        d.write(self.project/'brief.json',brief)
        self.assertIn('F1: context_illustration needs content sources, not style-only references',
                      w.preflight_report(self.project)['errors'])

    def test_external_context_respects_accepted_policy_and_needs_independent_review(self):
        self.add_context_visual();path=self.project/'design/style_profile.json';style=d.load(path)
        for policy in [{'enabled':False},
                       {'enabled':True,'purposes':['background'],'claim_boundary':'context_only',
                        'source_scope_precedence':True},
                       {'enabled':True,'purposes':['benchmark_context'],'claim_boundary':'context_only',
                        'source_scope_precedence':False}]:
            with self.subTest(policy=policy):
                d.write(path,dict(style,external_visuals=policy))
                self.assertEqual(w.preflight_report(self.project)['status'],'fail')
        d.write(path,dict(style,external_visuals={
            'enabled':True,'purposes':['benchmark_context'],'claim_boundary':'context_only',
            'source_scope_precedence':True}))
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        args=mock_review_fixture(self.project);review=d.load(args.review)
        self.assertTrue(all(row['external_visual_provenance']=='pending' for row in review['slides']))
        self.assertEqual(w.gate(args),1)
        for row in review['slides']:row['external_visual_provenance']='pass'
        d.write(args.review,review);self.assertEqual(w.gate(args),0)
        asset=d.load(self.project/'analysis/figure_manifest.json')['figures'][0]
        resources=d.load(args.handoff/'manifest.json')['resources']
        self.assertEqual(resources[asset['path']],asset['sha256'])
        (self.project/asset['path']).write_bytes(b'Changed synthetic context')
        self.assertIn(f'Changed source/asset: {asset["path"]}',w.contract_errors(self.project,args.handoff))


if __name__=='__main__':unittest.main()
