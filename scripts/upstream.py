#!/usr/bin/env python3
"""Maintain the current ppt-master submodule. No backend execution or remote writes."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SUB='third_party/ppt-master'
EXPECTED_URL='https://github.com/hugohe3/ppt-master.git'


def git(*args: str, cwd: Path=ROOT, check: bool=True) -> subprocess.CompletedProcess:
    result=subprocess.run(['git',*args],cwd=cwd,capture_output=True,text=True,timeout=240)
    if check and result.returncode:
        raise RuntimeError(f'git {args[0]} failed: {result.stderr.strip()}')
    return result


def contract() -> tuple[str,str]:
    top=git('rev-parse','--show-toplevel').stdout.strip()
    if Path(top).resolve()!=ROOT:raise RuntimeError('Not this repository root; restore/clone it first')
    url=git('config','-f','.gitmodules','--get','submodule.ppt-master.url').stdout.strip()
    path=git('config','-f','.gitmodules','--get','submodule.ppt-master.path').stdout.strip()
    branch=git('config','-f','.gitmodules','--get','submodule.ppt-master.branch').stdout.strip()
    if path!=SUB or url!=EXPECTED_URL or not branch:
        raise RuntimeError('Unexpected backend configuration; review .gitmodules explicitly')
    entry=git('ls-files','--stage','--',SUB).stdout.strip().split()
    if len(entry)<4 or entry[0]!='160000':raise RuntimeError('Backend is not a real gitlink submodule')
    return branch,entry[1]


def observe() -> dict:
    branch,recorded=contract();backend=ROOT/SUB
    result={'url':EXPECTED_URL,'path':str(backend),'tracking_branch':branch,
            'recorded_gitlink':recorded,'checked_at':datetime.now(timezone.utc).isoformat(),
            'initialized':(backend/'.git').exists(),'freshness':'not_checked_against_remote',
            'production_tested':False}
    if not result['initialized']:return result
    if Path(git('rev-parse','--show-toplevel',cwd=backend).stdout.strip()).resolve()!=backend:
        raise RuntimeError('Backend directory is not its own checkout')
    result['revision']=git('rev-parse','HEAD',cwd=backend).stdout.strip()
    result['dirty']=bool(git('status','--porcelain',cwd=backend).stdout.strip())
    license_path=backend/'LICENSE'
    text=license_path.read_text(encoding='utf-8') if license_path.is_file() else ''
    result['mit_license_observed']='MIT License' in text and 'Permission is hereby granted' in text
    result['entry_files']=[str(backend/p) for p in ['AGENTS.md','SKILL.md','skills/ppt-master/SKILL.md'] if (backend/p).is_file()]
    result['limits']='File/license probe only; read current instructions and test representative production pages.'
    return result


def update() -> dict:
    before=observe()
    if before.get('dirty'):raise RuntimeError('Dirty backend; save changes before updating. Nothing discarded.')
    if before.get('revision') and before['revision']!=before['recorded_gitlink']:
        raise RuntimeError('Unrecorded backend revision; inspect/commit the gitlink before another update')
    git('submodule','sync','--',SUB)
    # --remote follows .gitmodules branch rather than perpetually restoring the old gitlink.
    git('submodule','update','--init','--remote','--checkout','--depth','1','--',SUB)
    after=observe();after['freshness']='fetched_configured_branch_at_checked_at'
    if not after.get('mit_license_observed') or not after.get('entry_files'):
        raise RuntimeError('Updated backend needs license/entry review; no upstream code was executed or committed')
    after['previous_revision']=before.get('revision',before['recorded_gitlink'])
    after['gitlink_commit_needed']=after['revision']!=after['recorded_gitlink']
    return after


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['status','update']);parser.add_argument('--out',type=Path)
    args=parser.parse_args();record=update() if args.action=='update' else observe()
    text=json.dumps(record,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(text,encoding='utf-8')
    print(text,end='')
    return 0 if record['initialized'] else 2

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
