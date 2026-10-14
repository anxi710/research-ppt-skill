#!/usr/bin/env python3
"""Static public-repository checks. A heuristic, not a complete secret/license audit."""
from __future__ import annotations
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
DENIED={'.pdf','.pptx','.ppt','.docx','.zip','.ttf','.otf','.ttc','.woff','.woff2','.pem','.p12','.pfx'}
BANNED_DIRS={'workspaces','inputs','exports','renders','private','accepted_case'}

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
    if 'MIT License' not in (root/'LICENSE').read_text():errors.append('Expected MIT root license')
    return errors

if __name__=='__main__':
    try:
        errors=check();print(json.dumps({'status':'fail' if errors else 'pass','errors':errors,'limits':'Inspect the staged diff; this is a heuristic.'},indent=2));raise SystemExit(int(bool(errors)))
    except (OSError,subprocess.SubprocessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
