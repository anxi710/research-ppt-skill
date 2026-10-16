import contextlib
import copy
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from argparse import Namespace
from helpers import w,d,workspace,mock_review_fixture

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.sink=io.StringIO();self.ctx=contextlib.redirect_stdout(self.sink);self.ctx.__enter__();self.addCleanup(self.ctx.__exit__,None,None,None)
        self.project=workspace(Path(self.tmp.name))
    def test_fixture_preflight(self):self.assertEqual(w.preflight_report(self.project)['status'],'pass')
    def test_init_does_not_confirm_cli_values(self):
        project=Path(self.tmp.name)/'new-talk'
        w.init(Namespace(project=project,source=[Path(self.tmp.name)/'synthetic_source.md'],
                         template=None,minutes=2,language='en',audience='researchers'))
        brief=d.load(project/'brief.json')
        self.assertIsNone(brief['qa_time_included'])
        self.assertEqual(brief['intake_confirmation']['status'],'pending')
        self.assertEqual(brief['intake_confirmation']['user_response'],'')
        self.assertEqual(brief['presentation_type'],'research_report')
        self.assertEqual(brief['detail_level'],'detailed')
        self.assertEqual(w.preflight_report(project)['status'],'fail')
    def init_command(self, request_dir, *extra):
        return subprocess.run([sys.executable,w.__file__,'init',
                               '--source',os.path.relpath(Path(self.tmp.name)/'synthetic_source.md',request_dir),
                               '--minutes','2','--language','en','--audience','researchers',*extra],
                              cwd=request_dir,capture_output=True,text=True,check=True)
    def test_init_defaults_to_request_directory_and_source_name(self):
        request_dir=Path(self.tmp.name)/'request';request_dir.mkdir()
        result=self.init_command(request_dir)
        project=request_dir/'outputs/synthetic-source'
        self.assertEqual(Path(result.stdout.strip()),project)
        brief=d.load(project/'brief.json')
        self.assertEqual(brief['project_name'],'synthetic-source')
        self.assertEqual(brief['output_files']['pptx'],'exports/synthetic-source.pptx')
        self.assertEqual(brief['output_files']['speaker_notes'],'exports/synthetic-source-notes.md')
        self.assertEqual(brief['intake_confirmation']['status'],'pending')
    def test_init_unicode_name_stays_local_and_collisions_preserve_talks(self):
        request_dir=Path(self.tmp.name)/'request';request_dir.mkdir()
        result=self.init_command(request_dir,'--name','../中文 / 方法:讲解?')
        first=Path(result.stdout.strip())
        self.assertEqual(first,request_dir/'outputs/中文-方法-讲解')
        before=(first/'brief.json').read_bytes()
        # Even an empty pre-existing directory belongs to its caller.
        reserved=request_dir/'outputs/中文-方法-讲解-02';reserved.mkdir()
        result=self.init_command(request_dir,'--name','../中文 / 方法:讲解?')
        second=Path(result.stdout.strip())
        self.assertEqual(second,request_dir/'outputs/中文-方法-讲解-03')
        self.assertEqual((first/'brief.json').read_bytes(),before)
        self.assertEqual(list(reserved.iterdir()),[])
        brief=d.load(second/'brief.json')
        self.assertEqual(brief['project_name'],second.name)
        self.assertEqual(brief['output_files']['pdf'],f'exports/{second.name}-preview.pdf')
    def test_init_explicit_project_overrides_default_without_overwriting(self):
        project=Path(self.tmp.name)/'custom-location'
        args=Namespace(project=project,name='自定名称',
                       source=[Path(self.tmp.name)/'synthetic_source.md'],
                       template=None,minutes=2,language='en',audience='researchers')
        w.init(args)
        before=(project/'brief.json').read_bytes()
        self.assertEqual(d.load(project/'brief.json')['output_files']['pptx'],'exports/自定名称.pptx')
        with self.assertRaisesRegex(ValueError,'new/empty'):
            w.init(args)
        self.assertEqual((project/'brief.json').read_bytes(),before)
    def test_init_missing_source_creates_no_default_output(self):
        request_dir=Path(self.tmp.name)/'request';request_dir.mkdir()
        from unittest.mock import patch
        with patch.object(w.Path,'cwd',return_value=request_dir):
            with self.assertRaisesRegex(ValueError,'Every source must exist'):
                w.init(Namespace(project=None,name='topic',source=[request_dir/'missing.md'],
                                 template=None,minutes=2,language='en',audience='researchers'))
        self.assertFalse((request_dir/'outputs').exists())
    def test_init_respects_explicit_presentation_choices(self):
        request_dir=Path(self.tmp.name)/'request';request_dir.mkdir()
        result=self.init_command(request_dir,'--presentation-type','paper_talk','--detail-level','overview')
        brief=d.load(Path(result.stdout.strip())/'brief.json')
        self.assertEqual(brief['presentation_type'],'paper_talk')
        self.assertEqual(brief['detail_level'],'overview')
    def test_handoff_rejects_missing_or_pending_intake(self):
        path=self.project/'brief.json';brief=d.load(path)
        for record in [None,{'status':'pending'}, {'status':'confirmed','requirements':w.intake_requirements(brief),'user_response':''}]:
            with self.subTest(record=record):
                if record is None:brief.pop('intake_confirmation',None)
                else:brief['intake_confirmation']=record
                d.write(path,brief)
                with self.assertRaisesRegex(ValueError,'Intake:'):
                    w.handoff(Namespace(project=self.project,run_id='unconfirmed'))
                self.assertFalse((self.project/'handoff/unconfirmed').exists())
    def test_explicit_delegation_record_accepted(self):
        path=self.project/'brief.json';brief=d.load(path)
        brief['intake_confirmation'].update(status='delegated',user_response='SYNTHETIC FIXTURE ONLY: choose these settings and proceed without asking again.')
        d.write(path,brief)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
    def test_material_requirement_changes_invalidate_confirmation(self):
        path=self.project/'brief.json';original=d.load(path)
        changes={'audience':'new audience','target_minutes':3,'qa_time_included':True,
                 'qa_minutes':1,
                 'language':'zh-CN','purpose':'method tutorial','sections':['Methods'],
                 'style_intent':'different palette','deliverables':['pptx'],
                 'presentation_type':'paper_talk','detail_level':'overview'}
        for key,value in changes.items():
            with self.subTest(key=key):
                brief=copy.deepcopy(original);brief[key]=value;d.write(path,brief)
                self.assertTrue(any('requirements changed' in error for error in w.preflight_report(self.project)['errors']))
    def test_new_template_invalidates_confirmation(self):
        path=self.project/'brief.json';brief=d.load(path)
        template=dict(brief['sources'][0],id='STYLE',role='style_reference')
        brief['sources'].append(template);d.write(path,brief)
        self.assertTrue(any('requirements changed' in error for error in w.preflight_report(self.project)['errors']))
    def test_intake_rejects_incomplete_choices(self):
        path=self.project/'brief.json';original=d.load(path)
        for key,value in [('qa_time_included',None),('style_intent',''),('deliverables',[])]:
            with self.subTest(key=key):
                brief=copy.deepcopy(original);brief[key]=value;d.write(path,brief)
                with self.assertRaisesRegex(ValueError,'Intake:'):
                    w.intake(Namespace(project=self.project))
    def test_intake_summary_is_pending_after_changes(self):
        path=self.project/'brief.json';brief=d.load(path);brief['style_intent']='revised style';d.write(path,brief)
        w.intake(Namespace(project=self.project));updated=d.load(path)
        self.assertEqual(updated['intake_confirmation']['status'],'pending')
        self.assertEqual(updated['intake_confirmation']['user_response'],'')
        self.assertEqual(updated['intake_confirmation']['requirements']['style_intent'],'revised style')
        # A reviewed style profile still cannot stand in for user confirmation.
        self.assertEqual(d.load(self.project/'design/style_profile.json')['review_status'],'verified')
        self.assertEqual(w.preflight_report(self.project)['status'],'fail')
    def test_intake_preserves_unchanged_confirmation(self):
        path=self.project/'brief.json';before=path.read_bytes()
        w.intake(Namespace(project=self.project))
        self.assertEqual(path.read_bytes(),before)
    def test_legacy_intake_stays_accepted_without_new_report_fields(self):
        path=self.project/'brief.json';brief=d.load(path)
        for key in ['presentation_type','detail_level']:brief.pop(key)
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief)
        d.write(path,brief);before=path.read_bytes()
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        w.intake(Namespace(project=self.project))
        self.assertEqual(path.read_bytes(),before)
        w.handoff(Namespace(project=self.project,run_id='legacy'))
        snapshot=d.load(self.project/'handoff/legacy/brief.json')
        self.assertNotIn('presentation_type',snapshot)
        self.assertNotIn('detail_level',snapshot)
    def test_invalid_report_choices_fail_intake_cleanly(self):
        path=self.project/'brief.json';original=d.load(path)
        for key in ['presentation_type','detail_level']:
            for value in [None,'','unsupported',[],{}]:
                with self.subTest(key=key,value=value):
                    brief=copy.deepcopy(original);brief[key]=value;d.write(path,brief)
                    with self.assertRaisesRegex(ValueError,'invalid '+key):
                        w.intake(Namespace(project=self.project))
    def test_report_depth_change_returns_to_pending(self):
        path=self.project/'brief.json';brief=d.load(path)
        brief['detail_level']='overview';d.write(path,brief)
        w.intake(Namespace(project=self.project));updated=d.load(path)
        self.assertEqual(updated['intake_confirmation']['status'],'pending')
        self.assertEqual(updated['intake_confirmation']['user_response'],'')
        self.assertEqual(updated['intake_confirmation']['requirements']['detail_level'],'overview')
    def test_mixed_material_report_handoff_preserves_synthesis_provenance(self):
        root=Path(self.tmp.name)
        note=root/'reading_note.md';note.write_text('# Synthetic reading note\nCompare the teaching example with the fixture log only.\n')
        results=root/'results.csv';results.write_text('condition,illustrative_sum\nsynthetic_only,5\n')
        project=root/'mixed-report'
        w.init(Namespace(project=project,source=[root/'synthetic_source.md',note,results],
                         template=None,minutes=2,language='en',audience='researchers'))
        brief=d.load(project/'brief.json')
        brief.update(qa_time_included=False,style_intent='Synthetic neutral style; no institution')
        for source,role in zip(brief['sources'],['research_source','reading_note','user_result']):
            source.update(role=role,version='synthetic fixture v1')
        brief['intake_confirmation']={'status':'confirmed',
            'user_response':'SYNTHETIC FIXTURE ONLY: fictional acceptance of mixed-material report settings.',
            'requirements':w.intake_requirements(brief)}
        d.write(project/'brief.json',brief)
        claims=[{'id':'C1','kind':'source_claim','statement':'The synthetic teaching example says two plus three is five.',
                 'source_ids':['S1'],'locator':'S1: line 2','review_status':'verified'},
                {'id':'C2','kind':'source_claim','statement':'The illustrative fixture log records five.',
                 'source_ids':['S3'],'locator':'S3: results.csv, row 2, illustrative_sum column','review_status':'verified'},
                {'id':'C3','kind':'presenter_analysis','statement':'The synthetic log matches the teaching example; this is not a scientific result.',
                 'source_ids':['S1','S2','S3'],'locator':'S1: line 2; S2: line 2; S3: results.csv, row 2, illustrative_sum column',
                 'conditions':['Synthetic arithmetic fixture only'],'limitations':['No empirical inference'],
                 'review_status':'verified'}]
        d.write(project/'analysis/evidence.json',{'claims':claims})
        style=d.load(project/'design/style_profile.json');style['review_status']='verified'
        style['template_reference']['status']='selected'
        style['section_navigation']['sections']=[{'id':'comparison','label':'Synthetic comparison'}]
        d.write(project/'design/style_profile.json',style)
        plan=d.load(self.project/'design/slide_plan.json')
        backup=copy.deepcopy(plan['slides'][1]);backup['id']='P03';plan['slides'].append(backup)
        plan['slides'][0]['seconds']=15
        plan['slides'][1].update(hidden=False,seconds=105)
        for slide in plan['slides']:
            slide.update(evidence_ids=['C1','C2','C3'],display_title='Synthetic comparison')
            if slide['id']!='P01':slide['section_id']='comparison'
        plan['coverage']=[{'topic':'Synthetic teaching/log comparison','source_ids':['S1','S2','S3'],
                           'slide_ids':['P01','P02','P03'],'disposition':'main_and_backup',
                           'rationale':'UNIT TEST ONLY: demonstrate mixed-material provenance.'}]
        d.write(project/'design/slide_plan.json',plan)
        self.assertEqual(w.preflight_report(project)['status'],'pass')
        w.handoff(Namespace(project=project,run_id='mixed'))
        handoff_dir=project/'handoff/mixed'
        self.assertEqual(d.load(handoff_dir/'brief.json')['intake_confirmation']['requirements'],w.intake_requirements(brief))
        self.assertEqual(d.load(handoff_dir/'design/slide_plan.json')['coverage'],plan['coverage'])
        self.assertEqual(d.load(handoff_dir/'analysis/evidence.json')['claims'][2]['source_ids'],['S1','S2','S3'])
        self.assertIn('research_report',(handoff_dir/'handoff.md').read_text())
        (project/brief['sources'][2]['path']).write_text('condition,illustrative_sum\nsynthetic_only,6\n')
        self.assertTrue(w.contract_errors(project,handoff_dir))
    def test_evidence_metadata_does_not_reopen_intake(self):
        path=self.project/'brief.json';brief=d.load(path)
        brief['sources'][0]['version']='synthetic version clarified, same supplied bytes'
        brief['assumptions'].append('Synthetic detail discovered during source reading')
        d.write(path,brief)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
    def test_included_qa_reserves_speaking_time(self):
        path=self.project/'brief.json';brief=d.load(path)
        brief.update(target_minutes=25,qa_time_included=True,qa_minutes=5)
        brief['intake_confirmation']['requirements']=w.intake_requirements(brief)
        d.write(path,brief)
        plan=self.project/'design/slide_plan.json';slides=d.load(plan)
        slides['slides'][0]['seconds']=1200;d.write(plan,slides)
        # Twenty minutes of slides plus five reserved for Q&A fit the total budget.
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        slides['slides'][0]['seconds']=1500;d.write(plan,slides)
        self.assertTrue(any('speaking budget' in error for error in w.preflight_report(self.project)['errors']))
    def test_included_qa_requires_valid_reservation(self):
        path=self.project/'brief.json';original=d.load(path)
        for minutes in [None,0,-1,2,3,True]:
            with self.subTest(minutes=minutes):
                brief=copy.deepcopy(original);brief.update(qa_time_included=True,qa_minutes=minutes);d.write(path,brief)
                with self.assertRaisesRegex(ValueError,'Q&A minutes'):
                    w.intake(Namespace(project=self.project))
    def test_claim_without_locator_fails(self):
        p=self.project/'analysis/evidence.json';v=d.load(p);v['claims'][0].update(kind='source_claim',locator='');d.write(p,v)
        self.assertEqual(w.preflight_report(self.project)['status'],'fail')
    def test_pending_style_fails(self):
        d.write(self.project/'design/style_profile.json',{'review_status':'pending'});self.assertEqual(w.preflight_report(self.project)['status'],'fail')
    def test_unknown_visual_fails(self):
        p=self.project/'design/slide_plan.json';v=d.load(p);v['slides'][0]['primary_visual']['asset_ids']=['missing'];d.write(p,v)
        self.assertEqual(w.preflight_report(self.project)['status'],'fail')
    def test_handoff_immutable(self):
        args=Namespace(project=self.project,run_id='one');w.handoff(args)
        with self.assertRaises(ValueError):w.handoff(args)
    def test_handoff_carries_named_delivery_paths(self):
        brief=d.load(self.project/'brief.json')
        # Saved user/legacy filenames remain authoritative after defaults change.
        brief['output_files']['pdf']='exports/previous-custom-name.pdf'
        path=self.project/'brief.json';d.write(path,brief);before=path.read_bytes()
        w.handoff(Namespace(project=self.project,run_id='named'))
        self.assertEqual(path.read_bytes(),before)
        handoff_dir=self.project/'handoff/named'
        self.assertEqual(d.load(handoff_dir/'brief.json')['output_files'],brief['output_files'])
        text=(handoff_dir/'handoff.md').read_text()
        for path in brief['output_files'].values():self.assertIn(path,text)
    def test_source_mutation_invalidates(self):
        w.handoff(Namespace(project=self.project,run_id='one'))
        (self.project/'inputs/source_01.md').write_text('changed')
        self.assertTrue(w.contract_errors(self.project,self.project/'handoff/one'))
    def test_contract_mutation_invalidates(self):
        w.handoff(Namespace(project=self.project,run_id='one'))
        p=self.project/'design/slide_plan.json';p.write_text(p.read_text()+'\n')
        self.assertTrue(w.contract_errors(self.project,self.project/'handoff/one'))
    def test_unit_gate_positive_control(self):self.assertEqual(w.gate(mock_review_fixture(self.project)),0)
    def test_gate_rejects_pending_review(self):
        a=mock_review_fixture(self.project);v=d.load(a.review);v['slides'][0]['facts']='pending';d.write(a.review,v)
        self.assertEqual(w.gate(a),1)
    def test_gate_rejects_missing_backup_review(self):
        a=mock_review_fixture(self.project);v=d.load(a.review);v['slides'].pop();d.write(a.review,v)
        self.assertEqual(w.gate(a),1)
    def test_gate_rejects_unrelated_image(self):
        a=mock_review_fixture(self.project);v=d.load(a.review);v['slides'][0]['render_path']='not-the-render.png';d.write(a.review,v)
        self.assertEqual(w.gate(a),1)
    def test_gate_rejects_stale_receipt(self):
        a=mock_review_fixture(self.project);v=d.load(a.receipt);v['pptx_sha256']='old';d.write(a.receipt,v)
        self.assertEqual(w.gate(a),1)
    def test_review_seed_is_pending(self):
        a=mock_review_fixture(self.project);target=self.project/'qa/new_review.json'
        w.review_init(Namespace(project=self.project,pptx=a.pptx,handoff=a.handoff,render_report=a.render_report,out=target))
        v=d.load(target);self.assertFalse(v['reviewer']);self.assertTrue(all(r['visual']=='pending' for r in v['slides']))

if __name__=='__main__':unittest.main()
