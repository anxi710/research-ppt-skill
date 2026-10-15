from pathlib import Path
from html import escape
import tempfile
import unittest
from urllib.parse import urlencode
from scripts.check_repo import check_versions
ROOT=Path(__file__).resolve().parents[1]

class RepositoryTests(unittest.TestCase):
    def test_generic_skill_metadata_and_no_production_exporter(self):
        text=(ROOT/'skills/research-ppt/SKILL.md').read_text()
        self.assertIn('name: research-ppt',text);self.assertIn('license: MIT',text)
        self.assertFalse(list((ROOT/'skills/research-ppt').rglob('svg_to_pptx.py')))
        self.assertFalse(list(ROOT.rglob('ppt_master_compat*')))
    def test_submodule_configuration(self):
        text=(ROOT/'.gitmodules').read_text();self.assertIn('branch = main',text);self.assertIn('https://github.com/hugohe3/ppt-master.git',text)

class VersionContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'skills/research-ppt').mkdir(parents=True)
    def fixture(self,version='1.2.3',badge=None,release=None,html=True,image_version=None):
        badge=version if badge is None else badge
        release=version if release is None else release
        image_version=version if image_version is None else image_version
        (self.root/'skills/research-ppt/SKILL.md').write_text(
            f'---\nname: research-ppt\nmetadata:\n  version: "{version}"\n---\n# Synthetic skill\n',encoding='utf-8')
        src='https://img.shields.io/static/v1?'+urlencode({'label':'Skill','message':f'v{image_version}','color':'2563eb'})
        image=(f'<img src="{escape(src)}" alt="Skill v{badge}">' if html else
               f'![Skill v{badge}]({src})')
        (self.root/'README.md').write_text(f'# Synthetic repository\n{image}\n',encoding='utf-8')
        (self.root/'CHANGELOG.md').write_text(
            f'# Changelog\n\n## Unreleased\n\n- Pending changes.\n\n## {release} - 2026-01-01\n\n- Synthetic release.\n\n## 0.1.0\n',encoding='utf-8')
    def test_aligned_release_accepts_html_and_markdown_badges(self):
        for html in (True,False):
            with self.subTest(html=html):
                self.fixture(html=html)
                self.assertEqual(check_versions(self.root),[])
    def test_outdated_badge_is_rejected(self):
        self.fixture(badge='1.2.2')
        self.assertTrue(any('README.md Skill badge' in error for error in check_versions(self.root)))
    def test_outdated_image_is_rejected_even_when_alt_matches(self):
        for html in (True,False):
            with self.subTest(html=html):
                self.fixture(image_version='1.2.2',html=html)
                self.assertTrue(any('Skill badge image message' in error for error in check_versions(self.root)))
    def test_unreleased_does_not_hide_outdated_numbered_release(self):
        self.fixture(release='1.2.2')
        self.assertTrue(any('Latest CHANGELOG.md' in error for error in check_versions(self.root)))
    def test_invalid_semver_is_rejected(self):
        for version in ('01.2.3','1.02.3','1.2.03','1.2.3-01','v1.2.3','1.2','1.2.3-'):
            with self.subTest(version=version):
                self.fixture(version=version)
                self.assertTrue(any('SemVer 2.0' in error for error in check_versions(self.root)))
    def test_prerelease_and_build_metadata_are_valid(self):
        for version in ('1.2.3-rc.1','1.2.3-alpha.01a+build.001','1.2.3+20261015'):
            for html in (True,False):
                with self.subTest(version=version,html=html):
                    self.fixture(version=version,release=f'[{version}]',html=html)
                    self.assertEqual(check_versions(self.root),[])
if __name__=='__main__':unittest.main()
