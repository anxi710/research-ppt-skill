import contextlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from argparse import Namespace
from helpers import d,workspace,deck

class MaterialTests(unittest.TestCase):
    def test_page_ranges(self):
        self.assertEqual(d.parse_pages('1,3-5',5),[1,3,4,5])
        for s in ['0','6','4-2']:
            with self.assertRaises(ValueError):d.parse_pages(s,5)
    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):d.under(Path(t),'../escape')
    def test_pdf_crop_size_and_rotation(self):
        import pypdfium2 as pdfium
        from PIL import Image
        with tempfile.TemporaryDirectory() as t, contextlib.redirect_stdout(io.StringIO()):
            root=Path(t);pdf=root/'source.pdf';doc=pdfium.PdfDocument.new();page=doc.new_page(300,200);page.close();doc.save(str(pdf));doc.close()
            man=root/'figures.json';d.write(man,{'figures':[{'id':'F1','pdf_page':1,'bbox_pt':[20,20,280,100]}]})
            d.crop(Namespace(pdf=pdf,manifest=man,out=root/'crops',dpi=144))
            with Image.open(root/'crops/F1.png') as image:self.assertEqual(image.size,(520,160))
            report=d.load(root/'crops/crop_report.json');self.assertEqual(report[0]['visual_review'],'pending')
            d.write(man,{'figures':[{'id':'F1','pdf_page':1,'bbox_pt':[-1,20,280,100]}]})
            with self.assertRaises(ValueError):d.crop(Namespace(pdf=pdf,manifest=man,out=root/'bad',dpi=144))
    def test_notes_and_hidden_audit(self):
        with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()):
            p=workspace(Path(t));path=deck(p);r=d.audit_pptx(path,p/'design/slide_plan.json')
            self.assertEqual(r['machine_status'],'pass');self.assertEqual(r['hidden_slides'],1);self.assertEqual(r['planned_seconds'],120)
    def test_missing_notes_detected(self):
        from pptx import Presentation
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'no_notes.pptx';prs=Presentation();prs.slides.add_slide(prs.slide_layouts[6]);prs.save(path)
            self.assertEqual(d.audit_pptx(path)['machine_status'],'fail')

@unittest.skipUnless(os.environ.get('RUN_RENDER_TESTS')=='1' and (shutil.which('soffice') or shutil.which('libreoffice')),'Set RUN_RENDER_TESTS=1 with LibreOffice for a real synthetic rendering test')
class RenderTests(unittest.TestCase):
    def test_actual_renderer_covers_hidden_without_mutating_source(self):
        with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()):
            root=Path(t);p=workspace(root);path=deck(p);before=d.sha256(path)
            d.render_pptx(Namespace(pptx=path,out=p/'qa/all',include_hidden=True,dpi=96,libreoffice=None))
            all_report=d.load(p/'qa/all/render_report.json');self.assertEqual(all_report['slide_mapping'],[1,2]);self.assertEqual(all_report['pdf_pages'],2)
            d.render_pptx(Namespace(pptx=path,out=p/'qa/main',include_hidden=False,dpi=96,libreoffice=None))
            main=d.load(p/'qa/main/render_report.json');self.assertEqual(main['slide_mapping'],[1]);self.assertEqual(main['pdf_pages'],1)
            self.assertEqual(d.sha256(path),before)

if __name__=='__main__':unittest.main()
