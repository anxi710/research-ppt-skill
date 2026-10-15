"""Synthetic communication-contract checks; no private deck or research claims."""
import contextlib
import copy
import io
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from helpers import w, d, workspace, mock_review_fixture


class CommunicationContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.sink=io.StringIO()
        self.redirect=contextlib.redirect_stdout(self.sink)
        self.redirect.__enter__();self.addCleanup(self.redirect.__exit__,None,None,None)
        self.project=workspace(Path(self.tmp.name))

    def add_contract(self):
        contract={'version':1,'citation_placement':'notes',
                  'rules':['Use a concise synthetic title.',
                           'Keep the synthetic-only qualification visible.']}
        path=self.project/'design/style_profile.json';style=d.load(path)
        style['communication_contract']=contract;d.write(path,style)
        path=self.project/'design/slide_plan.json';plan=d.load(path)
        for slide in plan['slides']:
            slide['display_title']='Synthetic illustration only'
        d.write(path,plan)
        return contract

    def test_new_init_seeds_pending_generic_contract(self):
        project=Path(self.tmp.name)/'new-talk'
        w.init(Namespace(project=project,source=[Path(self.tmp.name)/'synthetic_source.md'],
                         template=None,minutes=2,language='en',audience='researchers'))
        style=d.load(project/'design/style_profile.json')
        self.assertEqual(style['review_status'],'pending')
        contract=style['communication_contract']
        self.assertEqual(contract['version'],1)
        self.assertEqual(contract['citation_placement'],'compact_footer')
        self.assertEqual(w.communication_contract_errors(style),[])
        self.assertTrue(all(isinstance(rule,str) and rule.strip() for rule in contract['rules']))

    def test_legacy_style_and_review_remain_valid_without_display_titles(self):
        self.assertNotIn('communication_contract',d.load(self.project/'design/style_profile.json'))
        self.assertTrue(all('display_title' not in slide
                            for slide in d.load(self.project/'design/slide_plan.json')['slides']))
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')
        args=mock_review_fixture(self.project)
        self.assertEqual(w.gate(args),0)
        for row in d.load(args.review)['slides']:
            for key in ['audience_copy','reference_match']:self.assertNotIn(key,row)
        self.assertEqual(w.CHECKS,['visual','facts','sources','notes','crop_completeness'])

    def test_valid_contract_citation_choices(self):
        self.add_contract()
        path=self.project/'design/style_profile.json';style=d.load(path)
        for placement in ['compact_footer','notes','per_slide']:
            with self.subTest(placement=placement):
                style['communication_contract']['citation_placement']=placement;d.write(path,style)
                if placement=='per_slide':
                    plan_path=self.project/'design/slide_plan.json';plan=d.load(plan_path)
                    for slide,choice in zip(plan['slides'],['compact_footer','notes']):
                        slide['citation_placement']=choice
                    d.write(plan_path,plan)
                self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_invalid_contracts_fail_preflight(self):
        valid=self.add_contract()
        invalid=[None,[], 'v1',{},
                 dict(valid,version=True),dict(valid,version='1'),dict(valid,version=2),
                 dict(valid,citation_placement='unsupported'),dict(valid,citation_placement=[]),
                 dict(valid,rules=[]),dict(valid,rules=None),dict(valid,rules='a rule'),
                 dict(valid,rules=[' ']),dict(valid,rules=['valid',7])]
        path=self.project/'design/style_profile.json';original=d.load(path)
        for contract in invalid:
            with self.subTest(contract=contract):
                style=copy.deepcopy(original);style['communication_contract']=contract;d.write(path,style)
                report=w.preflight_report(self.project)
                self.assertEqual(report['status'],'fail')
                self.assertTrue(any('communication_contract' in error for error in report['errors']))

    def test_v1_requires_explicit_display_title_including_backups(self):
        self.add_contract()
        path=self.project/'design/slide_plan.json';original=d.load(path)
        for value in [None,'',' ',7]:
            with self.subTest(value=value):
                plan=copy.deepcopy(original);plan['slides'][1]['display_title']=value;d.write(path,plan)
                report=w.preflight_report(self.project)
                self.assertEqual(report['status'],'fail')
                self.assertIn('P02: display_title missing (planning fields are not display copy)',report['errors'])

    def test_v1_requires_explicit_text_blocks_including_backups(self):
        self.add_contract()
        path=self.project/'design/slide_plan.json';original=d.load(path)
        cases=[('missing',None),('null',None),('string','Synthetic only'),
               ('object',{}),('mixed',['Synthetic only',7]),('blank',[' ']),
               ('empty string',[''])]
        for name,value in cases:
            with self.subTest(case=name):
                plan=copy.deepcopy(original)
                if name=='missing':plan['slides'][1].pop('on_slide_text')
                else:plan['slides'][1]['on_slide_text']=value
                d.write(path,plan)
                report=w.preflight_report(self.project)
                self.assertEqual(report['status'],'fail')
                self.assertTrue(any(error.startswith('P02: on_slide_text must be an explicit list')
                                    for error in report['errors']))
        plan=copy.deepcopy(original);plan['slides'][1]['on_slide_text']=[];d.write(path,plan)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_legacy_plan_can_omit_display_text_blocks(self):
        path=self.project/'design/slide_plan.json';plan=d.load(path)
        for slide in plan['slides']:slide.pop('on_slide_text')
        d.write(path,plan)
        self.assertEqual(w.preflight_report(self.project)['status'],'pass')

    def test_per_slide_citations_require_concrete_placement_on_every_slide(self):
        self.add_contract()
        path=self.project/'design/style_profile.json';style=d.load(path)
        style['communication_contract']['citation_placement']='per_slide';d.write(path,style)
        path=self.project/'design/slide_plan.json';original=d.load(path)
        original['slides'][0]['citation_placement']='compact_footer'
        cases=[('missing',None),('null',None),('empty',''),('recursive','per_slide'),
               ('unsupported','somewhere'),('list',[]),('object',{}),('boolean',True)]
        for name,value in cases:
            with self.subTest(case=name):
                plan=copy.deepcopy(original)
                if name=='missing':plan['slides'][1].pop('citation_placement',None)
                else:plan['slides'][1]['citation_placement']=value
                d.write(path,plan)
                report=w.preflight_report(self.project)
                self.assertEqual(report['status'],'fail')
                self.assertIn('P02: per_slide citation policy requires citation_placement compact_footer or notes',
                              report['errors'])

    def test_metrics_report_characters_without_density_approval(self):
        self.add_contract()
        path=self.project/'design/slide_plan.json';plan=d.load(path)
        plan['slides'][0]['display_title']='合成示例'
        plan['slides'][0]['on_slide_text']=['A','B','C','D','E']
        plan['slides'][1]['on_slide_text']=['Long synthetic text '*100]
        d.write(path,plan)
        report=w.preflight_report(self.project)
        self.assertEqual(report['status'],'pass')
        self.assertEqual(report['warnings'],[])
        self.assertEqual(report['display_text_metrics'][0],
                         {'slide_id':'P01','title_characters':4,'total_characters':9,'text_block_count':5})
        self.assertEqual(report['display_text_metrics'][1]['text_block_count'],1)
        self.assertGreater(report['display_text_metrics'][1]['total_characters'],1000)
        self.assertIn('informational, not density approval',report['meaning'])

    def test_review_init_seeds_pending_communication_checks(self):
        self.add_contract();args=mock_review_fixture(self.project)
        target=self.project/'qa/new_review.json'
        w.review_init(Namespace(project=self.project,pptx=args.pptx,handoff=args.handoff,
                                render_report=args.render_report,out=target))
        review=d.load(target)
        self.assertFalse(review['reviewer'])
        for row in review['slides']:
            for check in w.CHECKS+['audience_copy','reference_match']:
                self.assertEqual(row[check],'pending')

    def test_gate_requires_communication_review_for_every_slide(self):
        self.add_contract();args=mock_review_fixture(self.project)
        # The existing fixture passes every legacy check, but performs no communication review.
        self.assertEqual(w.gate(args),1)
        errors=d.load(args.out)['errors']
        self.assertTrue(any('audience_copy not passed' in error for error in errors))
        self.assertTrue(any('reference_match not passed' in error for error in errors))
        review=d.load(args.review)
        for row in review['slides']:
            row.update(audience_copy='pass',reference_match='pass')
        d.write(args.review,review)
        self.assertEqual(w.gate(args),0)
        for check in ['audience_copy','reference_match']:
            with self.subTest(check=check):
                incomplete=copy.deepcopy(review);incomplete['slides'][1].pop(check)
                d.write(args.review,incomplete)
                self.assertEqual(w.gate(args),1)
                self.assertIn(f'Slide 2: {check} not passed',d.load(args.out)['errors'])

    def test_handoff_carries_communication_contract_and_copy_boundary(self):
        contract=self.add_contract()
        w.handoff(Namespace(project=self.project,run_id='communication'))
        handoff=self.project/'handoff/communication'
        self.assertEqual(d.load(handoff/'design/style_profile.json')['communication_contract'],contract)
        self.assertEqual(d.load(handoff/'design/slide_plan.json')['slides'][0]['display_title'],
                         'Synthetic illustration only')
        text=(handoff/'handoff.md').read_text()
        for fragment in ['`display_title` and `on_slide_text` as the exact display copy',
                         'Layout, line breaks and mathematically equivalent typesetting may be adjusted',
                         'Changed wording requires updated preparation and a fresh handoff',
                         'not automatically visible text','"citation_placement": "notes"',
                         'even when bibliographic citations are placed in notes',
                         'audience_copy','reference_match',*contract['rules']]:
            self.assertIn(fragment,text)


if __name__=='__main__':unittest.main()
