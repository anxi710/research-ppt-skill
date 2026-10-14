import contextlib
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
