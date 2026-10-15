from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from html import escape
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

from scripts import bump_version
from scripts.check_repo import check_versions


ROOT = Path(__file__).resolve().parents[1]
DAY = date(2026, 10, 15)


class BumpVersionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'skills/research-ppt').mkdir(parents=True)
        self.fixture()

    def fixture(self, version='1.2.3', html=True, bracketed=False):
        self.skill = self.root / 'skills/research-ppt/SKILL.md'
        self.readme = self.root / 'README.md'
        self.changelog = self.root / 'CHANGELOG.md'
        self.skill.write_text(
            f'---\nname: research-ppt\nmetadata:\n  version: "{version}"\n---\n'
            f'# Synthetic skill\n\nExample of a historical version: {version}.\n', encoding='utf-8')
        src = 'https://img.shields.io/static/v1?' + urlencode(
            {'label': 'Skill', 'message': f'v{version}', 'color': '2563eb'})
        badge = (f'<img src="{escape(src)}" alt="Skill v{version}" height="20">' if html
                 else f'![Skill v{version}]({src})')
        self.readme.write_text(f'# Synthetic repository\n{badge}\n\nOld example: {version}\n', encoding='utf-8')
        pending = '[Unreleased]' if bracketed else 'Unreleased'
        release = f'[{version}]' if bracketed else version
        self.payload = '\n\n### Added\n\n- Synthetic capability.\n- 中文维护说明。\n\n'
        self.history = f'## {release} - 2026-01-01\n\n- Original release.\n\n## 0.1.0\n\n- Older history.\n'
        self.changelog.write_text(f'# Changelog\n\n## {pending}' + self.payload + self.history, encoding='utf-8')

    def snapshot(self):
        return {path.relative_to(self.root): path.read_bytes()
                for path in self.root.rglob('*') if path.is_file()}

    def test_named_increments_sync_files_and_preserve_history(self):
        for increment, target in (('patch', '1.2.4'), ('minor', '1.3.0'), ('major', '2.0.0')):
            with self.subTest(increment=increment):
                self.fixture()
                plan = bump_version.prepare_bump(self.root, increment, DAY)
                bump_version.apply_bump(plan)
                self.assertEqual(plan.target, target)
                self.assertEqual(check_versions(self.root), [])
                self.assertIn(f'## {target} - 2026-10-15' + self.payload + self.history,
                              self.changelog.read_text(encoding='utf-8'))
                self.assertIn('## Unreleased\n\n## ', self.changelog.read_text(encoding='utf-8'))
                self.assertIn('Example of a historical version: 1.2.3.', self.skill.read_text())
                self.assertIn('Old example: 1.2.3', self.readme.read_text())

    def test_prerelease_build_urls_and_bracketed_changelog(self):
        for html in (True, False):
            with self.subTest(html=html):
                self.fixture(html=html, bracketed=True)
                target = '1.3.0-rc.1+build.001'
                bump_version.apply_bump(bump_version.prepare_bump(self.root, target, DAY))
                self.assertEqual(check_versions(self.root), [])
                self.assertIn('v1.3.0-rc.1%2Bbuild.001', self.readme.read_text())
                if html:
                    self.assertIn('&amp;message=', self.readme.read_text())
                self.assertIn(f'## [{target}] - 2026-10-15' + self.payload + self.history,
                              self.changelog.read_text())

    def test_precedence_uses_numeric_components_and_prerelease_rules(self):
        for current, target in (('1.9.9', '1.10.0'), ('1.2.3-rc.2', '1.2.3-rc.10'),
                                ('1.2.3-rc.10', '1.2.3'), ('1.2.3-alpha', '1.2.3-alpha.1'),
                                ('1.2.3-9', '1.2.3-alpha')):
            with self.subTest(current=current, target=target):
                self.fixture(version=current)
                bump_version.apply_bump(bump_version.prepare_bump(self.root, target, DAY))
                self.assertEqual(check_versions(self.root), [])

    def test_named_increment_clears_suffixes(self):
        self.fixture(version='1.2.3-rc.1+build.5')
        plan = bump_version.prepare_bump(self.root, 'patch', DAY)
        bump_version.apply_bump(plan)
        self.assertEqual(plan.target, '1.2.4')
        self.assertEqual(check_versions(self.root), [])

    def test_dry_run_prints_diff_without_creating_or_changing_files(self):
        before = self.snapshot()
        output = io.StringIO()
        with redirect_stdout(output):
            result = bump_version.main(['minor', '--root', str(self.root), '--dry-run', '--date', '2026-10-15'])
        self.assertEqual(result, 0)
        self.assertEqual(self.snapshot(), before)
        self.assertIn('1.2.3 -> 1.3.0', output.getvalue())
        self.assertIn('+++ b/CHANGELOG.md', output.getvalue())
        self.assertIn('+## 1.3.0 - 2026-10-15', output.getvalue())

    def test_rejects_invalid_or_non_increasing_versions_without_writes(self):
        for target in ('v1.3.0', '1.03.0', '1.3', '1.3.0-01', '1.2.3', '1.2.2',
                       '1.2.3-rc.1', '1.2.3+build.2', '1.1.99', '1.2.3-alpha'):
            with self.subTest(target=target):
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    bump_version.prepare_bump(self.root, target, DAY)
                self.assertEqual(self.snapshot(), before)
        self.fixture(version='1.2.3-rc.10')
        with self.assertRaises(ValueError):
            bump_version.prepare_bump(self.root, '1.2.3-rc.2', DAY)

    def test_rejects_inconsistent_or_ambiguous_inputs_without_writes(self):
        mutations = (
            (self.readme, lambda text: text.replace('Skill v1.2.3', 'Skill v1.2.2')),
            (self.readme, lambda text: text.replace('&amp;message=v1.2.3', '&amp;message=v1.2.2')),
            (self.changelog, lambda text: text.replace('## Unreleased', '## Pending')),
            (self.changelog, lambda text: text.replace('## Unreleased', '## Unreleased\n\n## Unreleased')),
            (self.changelog, lambda text: text.replace(self.payload, '\n\n### Added\n\n')),
            (self.changelog, lambda text: text + '\n## 1.3.0\n\n- Duplicate target.\n'),
            (self.skill, lambda text: text.replace('  version: "1.2.3"', '  version: "1.2.3"\n  version: "1.2.3"')),
        )
        for path, mutate in mutations:
            with self.subTest(path=path, mutation=mutate):
                self.fixture()
                path.write_text(mutate(path.read_text()), encoding='utf-8')
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    bump_version.prepare_bump(self.root, 'minor', DAY)
                self.assertEqual(self.snapshot(), before)

    def test_updates_existing_translated_badges_without_adding_them(self):
        translated = self.root / 'README.zh-CN.md'
        translated.write_text(self.readme.read_text(), encoding='utf-8')
        plain = self.root / 'README.other.md'
        plain.write_text('# Synthetic README without a badge\n', encoding='utf-8')
        bump_version.apply_bump(bump_version.prepare_bump(self.root, 'minor', DAY))
        self.assertIn('Skill v1.3.0', translated.read_text())
        self.assertEqual(plain.read_text(), '# Synthetic README without a badge\n')

    def test_failure_after_one_replace_rolls_back_all_files(self):
        before = self.snapshot()
        plan = bump_version.prepare_bump(self.root, 'minor', DAY)
        real_replace = os.replace
        calls = 0

        def fail_once(src, dest):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('Synthetic replacement failure')
            return real_replace(src, dest)

        with patch.object(bump_version.os, 'replace', side_effect=fail_once):
            with self.assertRaisesRegex(OSError, 'Synthetic replacement failure'):
                bump_version.apply_bump(plan)
        self.assertEqual(self.snapshot(), before)

    def test_stale_plan_does_not_overwrite_a_later_edit(self):
        plan = bump_version.prepare_bump(self.root, 'minor', DAY)
        self.readme.write_text(self.readme.read_text() + '\nLater user edit.\n', encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'File changed'):
            bump_version.apply_bump(plan)
        self.assertEqual(self.snapshot(), before)

    def test_failed_rollback_keeps_original_backup_and_restores_other_files(self):
        before = self.snapshot()
        plan = bump_version.prepare_bump(self.root, 'minor', DAY)
        real_replace = os.replace
        calls = 0

        def fail_twice(src, dest):
            nonlocal calls
            calls += 1
            if calls in (3, 4):
                raise OSError(f'Synthetic failure {calls}')
            return real_replace(src, dest)

        with patch.object(bump_version.os, 'replace', side_effect=fail_twice):
            with self.assertRaisesRegex(OSError, 'Original backups have been kept'):
                bump_version.apply_bump(plan)
        self.assertEqual(calls, 5)
        self.assertEqual(self.skill.read_bytes(), before[self.skill.relative_to(self.root)])
        self.assertEqual(self.changelog.read_bytes(), before[self.changelog.relative_to(self.root)])
        backups = list(self.root.rglob('.bump-version-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), before[Path('README.md')])

    def test_crlf_and_file_permissions_are_preserved(self):
        for path in (self.skill, self.readme, self.changelog):
            path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        self.skill.chmod(0o640)
        bump_version.apply_bump(bump_version.prepare_bump(self.root, 'minor', DAY))
        self.assertEqual(check_versions(self.root), [])
        self.assertEqual(self.skill.stat().st_mode & 0o777, 0o640)
        for path in (self.skill, self.readme, self.changelog):
            self.assertNotIn(b'\n', path.read_bytes().replace(b'\r\n', b''))

    def test_cli_runs_outside_checkout_and_defaults_to_its_own_root(self):
        scripts = self.root / 'scripts'
        scripts.mkdir()
        for name in ('bump_version.py', 'check_repo.py'):
            shutil.copyfile(ROOT / 'scripts' / name, scripts / name)
        with tempfile.TemporaryDirectory() as outside:
            result = subprocess.run(
                [sys.executable, str(scripts / 'bump_version.py'), 'minor', '--date', '2026-10-15'],
                cwd=outside, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(check_versions(self.root), [])
        self.assertIn('## 1.3.0 - 2026-10-15', self.changelog.read_text())

    def test_bad_date_is_rejected_without_writes(self):
        for day in ('2026-02-30', '20261015', '2026-W42-4'):
            with self.subTest(day=day):
                before = self.snapshot()
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    bump_version.main(['minor', '--root', str(self.root), '--date', day])
                self.assertEqual(error.exception.code, 2)
                self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
