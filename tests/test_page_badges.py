"""Synthetic native fields and lookalikes in actual PowerPoint packages."""
import tempfile
import unittest
from pathlib import Path

from pptx import Presentation
from helpers import add_badge, d


class BadgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'badges.pptx'
        self.prs = Presentation()
        self.slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.slide.notes_slide.notes_text_frame.text = 'Synthetic notes.'

    def badge(self, slide, ordinal):
        return add_badge(slide.shapes, self.prs, ordinal)

    def errors(self):
        self.prs.save(self.path)
        return d.audit_pptx(self.path, academic_navigator=True)['errors']

    def test_literal_badge_and_unrelated_field(self):
        section = self.badge(self.slide, 1)
        section.left = 0
        self.badge(self.slide, 1).text = '1'
        self.assertTrue(self.errors())
        self.assertFalse(d.audit_pptx(self.path)['errors'])

    def test_inherited_field_and_local_override(self):
        shape = self.badge(self.slide, 1)
        layout = self.slide.slide_layout
        for layer in (layout, layout.slide_master):
            layer.shapes._spTree.append(shape._element)
            self.assertFalse(self.errors())
        local = self.badge(self.slide, 1)
        local.text = '1'
        self.assertTrue(self.errors())

    def test_hidden_slide_in_presentation_order(self):
        self.badge(self.slide, 2)
        hidden = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        hidden.notes_slide.notes_text_frame.text = 'Backup notes.'
        hidden._element.set('show', '0')
        badge = self.badge(hidden, 1)
        order = self.prs.slides._sldIdLst
        order.insert(0, order[-1])
        self.assertFalse(self.errors())
        badge.text_frame.paragraphs[0].add_run().text = '/2'
        self.assertIn('Slide 1:', self.errors()[0])
