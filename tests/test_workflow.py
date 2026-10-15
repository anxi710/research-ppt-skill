import contextlib
import copy
import io
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
        self.assertEqual(w.preflight_report(project)['status'],'fail')
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
                 'style_intent':'different palette','deliverables':['pptx']}
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
