import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
import tempfile
import shutil
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

    def test_restore_bundle_preserves_working_files(self):
        spec=importlib.util.spec_from_file_location('restore_git',ROOT/'scripts/restore_git.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);seed=root/'seed';seed.mkdir();target=root/'target';target.mkdir()
            def git(*args):return subprocess.run(['git',*args],cwd=seed,capture_output=True,text=True,check=True)
            git('init','--initial-branch=main');git('config','user.name','Synthetic Test');git('config','user.email','test@example.invalid')
            (seed/'README.md').write_text('Original tracked content')
            git('add','README.md');git('commit','-m','synthetic test')
            bundle=target/'research-ppt-skill.bundle';git('bundle','create',str(bundle),'main')
            (target/'README.md').write_text('Local modification must survive')
            module.restore(target)
            self.assertEqual((target/'README.md').read_text(),'Local modification must survive')
            self.assertTrue((target/'third_party/ppt-master').is_dir())
            out=subprocess.run(['git','rev-parse','HEAD'],cwd=target,capture_output=True,text=True,check=True)
            self.assertEqual(out.stdout,git('rev-parse','HEAD').stdout)

if __name__=='__main__':unittest.main()
