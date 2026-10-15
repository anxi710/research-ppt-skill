#!/usr/bin/env python3
"""Static public-repository checks. A heuristic, not a complete secret/license audit."""
from __future__ import annotations
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
DENIED={'.pdf','.pptx','.ppt','.docx','.zip','.ttf','.otf','.ttc','.woff','.woff2','.pem','.p12','.pfx'}
BANNED_DIRS={'workspaces','inputs','outputs','exports','renders','private','accepted_case'}
_NUMERIC=r'(?:0|[1-9][0-9]*)'
_PRERELEASE=rf'(?:{_NUMERIC}|[0-9]*[A-Za-z-][0-9A-Za-z-]*)'
SEMVER=re.compile(rf'{_NUMERIC}\.{_NUMERIC}\.{_NUMERIC}'
                  rf'(?:-{_PRERELEASE}(?:\.{_PRERELEASE})*)?'
                  r'(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?')

def check_versions(root: Path) -> list[str]:
    """Keep release labels aligned with the skill's SemVer metadata."""
    skill=root/'skills/research-ppt/SKILL.md'
    if not skill.is_file():return ['Missing skill version metadata']
    frontmatter=re.match(r'---\n(.*?)\n---(?:\n|$)',skill.read_text(encoding='utf-8'),re.S)
    metadata=re.search(r'^metadata:[ \t]*\n((?:[ \t]+[^\n]*(?:\n|$))*)',
                       frontmatter.group(1),re.M) if frontmatter else None
    field=re.search(r'^[ \t]+version:[ \t]*([^\n]+)',metadata.group(1),re.M) if metadata else None
    version=field.group(1).strip() if field else ''
    if version[:1] in ('"',"'") and version[-1:]==version[:1]:version=version[1:-1]
    if not SEMVER.fullmatch(version):
        return [f'Skill metadata.version must be SemVer 2.0 without a v prefix: {version!r}']

    errors=[]
    readme=root/'README.md'
    if not readme.is_file():
        errors.append('Missing README.md Skill version badge')
    else:
        text=readme.read_text(encoding='utf-8')
        badges=re.findall(r'!\[Skill v([^\]\s]+)\]\(([^\s)]+)\)',text)
        for tag in re.findall(r'<img\b[^>]*>',text):
            alt=re.search(r'\balt\s*=\s*([\"\'])(.*?)\1',tag,re.S)
            if alt and alt.group(2).startswith('Skill v'):
                src=re.search(r'\bsrc\s*=\s*([\"\'])(.*?)\1',tag,re.S)
                badges.append((alt.group(2)[len('Skill v'):],src.group(2) if src else ''))
        if not badges:errors.append('Missing README.md Skill version badge')
        elif any(badge!=version for badge,_ in badges):
            errors.append(f'README.md Skill badge must match metadata.version {version}')
        for _,src in badges:
            url=urlparse(unescape(src));query=parse_qs(url.query)
            if (url.netloc!='img.shields.io' or url.path!='/static/v1' or
                query.get('label')!=['Skill'] or query.get('message')!=[f'v{version}']):
                errors.append(f'README.md Skill badge image message must match metadata.version v{version}')

    changelog=root/'CHANGELOG.md'
    if not changelog.is_file():
        errors.append('Missing CHANGELOG.md numbered release')
    else:
        # Unreleased is intentionally not a release; accept common bracketed headings.
        release=re.search(r'^##[ \t]+(?:\[([0-9][^\]\n]*)\]|([0-9][^\s\n]*))(?:[ \t]+.*)?$',
                          changelog.read_text(encoding='utf-8'),re.M)
        latest=(release.group(1) or release.group(2)) if release else ''
        if latest!=version:
            errors.append(f'Latest CHANGELOG.md numbered release must match metadata.version {version}; found {latest!r}')
    return errors

def check(root: Path=ROOT) -> list[str]:
    result=subprocess.run(['git','ls-files','--stage','-z'],cwd=root,capture_output=True,text=True,check=True)
    errors=[];paths=[];sub_found=False
    secret_patterns=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
    for entry in result.stdout.split('\0'):
        if not entry:continue
        metadata,name=entry.split('\t',1);mode=metadata.split()[0]
        if mode=='160000':
            if name!='third_party/ppt-master':errors.append(f'Unexpected submodule {name}')
            sub_found=True;continue
        path=root/name;paths.append(name)
        if path.is_symlink():errors.append(f'Public package must not include symlink: {name}');continue
        if path.suffix.lower() in DENIED or any(p in BANNED_DIRS for p in Path(name).parts):errors.append(f'Private/binary artifact: {name}')
        if path.name.startswith('.env') and path.name!='.env.example':errors.append(f'Environment file: {name}')
        if not path.is_file():errors.append(f'Missing tracked file: {name}');continue
        if path.stat().st_size>600_000:errors.append(f'Unexpectedly large file: {name}')
        try:text=path.read_text(encoding='utf-8')
        except UnicodeDecodeError:errors.append(f'Unexpected binary: {name}');continue
        for pattern in secret_patterns:
            if pattern.search(text):errors.append(f'Possible credential in {name}')
        if path.suffix=='.json':
            try:json.loads(text)
            except ValueError:errors.append(f'Invalid JSON: {name}')
    if not sub_found:errors.append('Missing real ppt-master gitlink (a .gitmodules URL is not sufficient)')
    skill=root/'skills/research-ppt/SKILL.md'
    if not skill.is_file() or not skill.read_text().startswith('---\nname: research-ppt\n'):errors.append('Skill metadata missing')
    errors.extend(check_versions(root))
    if 'MIT License' not in (root/'LICENSE').read_text():errors.append('Expected MIT root license')
    return errors

if __name__=='__main__':
    try:
        errors=check();print(json.dumps({'status':'fail' if errors else 'pass','errors':errors,'limits':'Inspect the staged diff; this is a heuristic.'},indent=2));raise SystemExit(int(bool(errors)))
    except (OSError,subprocess.SubprocessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
