import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]

class RepositoryTests(unittest.TestCase):
    def test_generic_skill_metadata_and_no_production_exporter(self):
        text=(ROOT/'skills/research-ppt/SKILL.md').read_text()
        self.assertIn('name: research-ppt',text);self.assertIn('license: MIT',text)
        self.assertFalse(list((ROOT/'skills/research-ppt').rglob('svg_to_pptx.py')))
        self.assertFalse(list(ROOT.rglob('ppt_master_compat*')))
    def test_submodule_configuration(self):
        text=(ROOT/'.gitmodules').read_text();self.assertIn('branch = main',text);self.assertIn('https://github.com/hugohe3/ppt-master.git',text)
    def test_publish_defaults_to_dry_run(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/publish_github.py')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0);self.assertIn('DRY RUN',r.stdout)

if __name__=='__main__':unittest.main()
