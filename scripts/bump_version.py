#!/usr/bin/env python3
"""Prepare a SemVer release without committing, tagging or publishing it."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import difflib
from html import escape, unescape
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

if __package__:
    from .check_repo import ROOT, SEMVER, check_versions
else:
    from check_repo import ROOT, SEMVER, check_versions


@dataclass(frozen=True)
class Change:
    path: Path
    before: bytes
    after: bytes


@dataclass(frozen=True)
class ReleasePlan:
    root: Path
    current: str
    target: str
    day: date
    changes: tuple[Change, ...]


def precedence(version: str) -> tuple:
    """SemVer precedence ignores build metadata and orders numeric IDs as numbers."""
    if not SEMVER.fullmatch(version):
        raise ValueError(f'Expected SemVer without a v prefix: {version!r}')
    core, separator, prerelease = version.split('+', 1)[0].partition('-')
    identifiers = tuple((0, int(part)) if part.isdigit() else (1, part)
                        for part in prerelease.split('.')) if separator else ()
    return (tuple(map(int, core.split('.'))), not separator, identifiers)


def next_version(current: str, target: str) -> str:
    current_key = precedence(current)
    if target in ('major', 'minor', 'patch'):
        core = list(current_key[0])
        index = ('major', 'minor', 'patch').index(target)
        core[index] += 1
        core[index + 1:] = [0] * (2 - index)
        target = '.'.join(map(str, core))
    if precedence(target) <= current_key:
        raise ValueError('Target version must increase SemVer precedence; '
                         'changing build metadata alone is not an increment')
    return target


def skill_version(text: str) -> tuple[str, int, int]:
    front = re.match(r'---\n(.*?)\n---(?:\n|$)', text, re.S)
    blocks = list(re.finditer(r'^metadata:[ \t]*\n((?:[ \t]+[^\n]*(?:\n|$))*)',
                              front.group(1), re.M)) if front else []
    if len(blocks) != 1:
        raise ValueError('Expected one frontmatter metadata block in SKILL.md')
    fields = list(re.finditer(r'^[ \t]+version:[ \t]*([^\n]+)', blocks[0].group(1), re.M))
    if len(fields) != 1:
        raise ValueError('Expected one metadata.version field in SKILL.md')
    raw = fields[0].group(1)
    value = raw.strip()
    quoted = value[:1] in ('"', "'") and value[-1:] == value[:1]
    version = value[1:-1] if quoted else value
    precedence(version)
    start = (front.start(1) + blocks[0].start(1) + fields[0].start(1)
             + len(raw) - len(raw.lstrip()) + int(quoted))
    return version, start, start + len(version)


def badge_url(src: str, current: str, target: str) -> str:
    url = urlsplit(unescape(src))
    pairs = parse_qsl(url.query, keep_blank_values=True)
    labels = [value for key, value in pairs if key == 'label']
    messages = [value for key, value in pairs if key == 'message']
    if (url.netloc != 'img.shields.io' or url.path != '/static/v1'
            or labels != ['Skill'] or messages != [f'v{current}']):
        raise ValueError('Skill badge image must match the current version')
    pairs = [(key, f'v{target}' if key == 'message' else value) for key, value in pairs]
    return urlunsplit(url._replace(query=urlencode(pairs, quote_via=quote)))


def update_badges(text: str, current: str, target: str) -> str:
    def html_badge(match: re.Match) -> str:
        tag = match.group(0)
        alt = re.search(r'\balt\s*=\s*([\"\'])(.*?)\1', tag, re.S)
        if not alt or not alt.group(2).startswith('Skill v'):
            return tag
        src = re.search(r'\bsrc\s*=\s*([\"\'])(.*?)\1', tag, re.S)
        if alt.group(2) != f'Skill v{current}' or not src:
            raise ValueError('Skill badge must match the current version and have an image URL')
        edits = [(alt.start(2), alt.end(2), f'Skill v{target}'),
                 (src.start(2), src.end(2), escape(badge_url(src.group(2), current, target)))]
        for start, end, value in sorted(edits, reverse=True):
            tag = tag[:start] + value + tag[end:]
        return tag

    def markdown_badge(match: re.Match) -> str:
        if match.group(1) != current:
            raise ValueError('Skill badge must match the current version')
        return f'![Skill v{target}]({badge_url(match.group(2), current, target)})'

    text = re.sub(r'<img\b[^>]*>', html_badge, text)
    return re.sub(r'!\[Skill v([^\]\s]+)\]\(([^\s)]+)\)', markdown_badge, text)


def release_changelog(text: str, target: str, day: date) -> str:
    headings = list(re.finditer(r'^##[ \t]+([^\n]+?)[ \t]*$', text, re.M))
    pending = [heading for heading in headings
               if heading.group(1) in ('Unreleased', '[Unreleased]')]
    if len(pending) != 1 or pending[0] != headings[0]:
        raise ValueError('CHANGELOG.md must start with one Unreleased section')
    if any(heading.group(1).split()[0].strip('[]') == target for heading in headings):
        raise ValueError(f'CHANGELOG.md already contains version {target}')
    end = headings[1].start() if len(headings) > 1 else len(text)
    body = text[pending[0].end():end]
    if not any(line.strip() and not line.lstrip().startswith('#') for line in body.splitlines()):
        raise ValueError('Unreleased has no changes to release')
    label = f'[{target}]' if pending[0].group(1).startswith('[') else target
    return (text[:pending[0].end()] + f'\n\n## {label} - {day.isoformat()}'
            + body + text[end:])


def prepare_bump(root: Path, target: str, day: date | None = None) -> ReleasePlan:
    root = root.resolve()
    errors = check_versions(root)
    if errors:
        raise ValueError('Fix version consistency before bumping:\n- ' + '\n- '.join(errors))
    originals: dict[Path, bytes] = {}
    endings: dict[Path, str] = {}

    def read(path: Path) -> str:
        if path.is_symlink():
            raise ValueError(f'Refusing to modify symlink: {path}')
        originals[path] = path.read_bytes()
        text = originals[path].decode('utf-8')
        endings[path] = '\r\n' if '\r\n' in text else '\n'
        return text.replace('\r\n', '\n')

    skill = root / 'skills/research-ppt/SKILL.md'
    text = read(skill)
    current, start, end = skill_version(text)
    target = next_version(current, target)
    day = day or date.today()
    updated = {skill: text[:start] + target + text[end:]}
    for readme in sorted(root.glob('README*.md')):
        updated[readme] = update_badges(read(readme), current, target)
    changelog = root / 'CHANGELOG.md'
    updated[changelog] = release_changelog(read(changelog), target, day)
    changes = tuple(Change(path, originals[path], text.replace('\n', endings[path]).encode('utf-8'))
                    for path, text in updated.items()
                    if text.replace('\n', endings[path]).encode('utf-8') != originals[path])
    return ReleasePlan(root, current, target, day, changes)


def apply_bump(plan: ReleasePlan) -> None:
    """Stage all contents first; restore replaced files if any write/check fails."""
    staged: list[Path] = []
    replacements: list[tuple[Change, Path, Path]] = []
    applied: list[tuple[Change, Path]] = []
    retained: set[Path] = set()

    def stage(change: Change, data: bytes) -> Path:
        descriptor, name = tempfile.mkstemp(prefix='.bump-version-', dir=change.path.parent)
        path = Path(name)
        staged.append(path)
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
        path.chmod(stat.S_IMODE(change.path.stat().st_mode))
        return path

    try:
        for change in plan.changes:
            if change.path.read_bytes() != change.before:
                raise ValueError(f'File changed while preparing release: {change.path}')
            replacements.append((change, stage(change, change.after), stage(change, change.before)))
        for change, replacement, backup in replacements:
            if change.path.read_bytes() != change.before:
                raise ValueError(f'File changed while preparing release: {change.path}')
            os.replace(replacement, change.path)
            applied.append((change, backup))
        errors = check_versions(plan.root)
        if errors:
            raise ValueError('Updated version check failed:\n- ' + '\n- '.join(errors))
    except Exception as error:
        recovery_errors = []
        for change, backup in reversed(applied):
            try:
                os.replace(backup, change.path)
            except OSError as restore_error:
                retained.add(backup)
                recovery_errors.append(f'{change.path}: {restore_error}; original backup: {backup}')
        if recovery_errors:
            raise OSError(f'Release update failed ({error}); some files could not be restored. '
                          'Original backups have been kept:\n- ' + '\n- '.join(recovery_errors)) from error
        raise
    finally:
        for path in staged:
            if path not in retained:
                path.unlink(missing_ok=True)


def iso_date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Expected a valid YYYY-MM-DD date') from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError('Expected a valid YYYY-MM-DD date')
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', help='patch, minor, major, or an explicit SemVer (without v)')
    parser.add_argument('--dry-run', action='store_true', help='print the diff without writing files')
    parser.add_argument('--date', type=iso_date, default=None, help='release date, YYYY-MM-DD (default: today)')
    parser.add_argument('--root', type=Path, default=ROOT, help='repository root (default: script location)')
    args = parser.parse_args(argv)
    try:
        plan = prepare_bump(args.root, args.target, args.date)
        print(f'{"Preview" if args.dry_run else "Preparing"}: {plan.current} -> {plan.target} ({plan.day})')
        if args.dry_run:
            for change in plan.changes:
                name = change.path.relative_to(plan.root).as_posix()
                print(''.join(difflib.unified_diff(
                    change.before.decode('utf-8').splitlines(keepends=True),
                    change.after.decode('utf-8').splitlines(keepends=True),
                    fromfile=f'a/{name}', tofile=f'b/{name}')), end='')
        else:
            apply_bump(plan)
            for change in plan.changes:
                print(f'Updated {change.path.relative_to(plan.root)}')
        return 0
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
