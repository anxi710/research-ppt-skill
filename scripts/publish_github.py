#!/usr/bin/env python3
"""Explicitly create a NEW public GitHub skill repository with an authenticated gh CLI.

Dry-run by default. No overwrites, force pushes, automatic credentials, or private assets.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from restore_git import restore
from check_repo import check
from upstream import update, SUB

ROOT=Path(__file__).resolve().parents[1]


def run(argv: list[str],check_return: bool=True) -> subprocess.CompletedProcess:
    result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=300)
    if check_return and result.returncode:
        raise RuntimeError(f'{argv[0]} {argv[1]} failed: {result.stderr.strip()}')
    return result


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',default='research-ppt-skill')
    p.add_argument('--owner',help='Must match the authenticated personal account; omitted means current user')
    p.add_argument('--publish',action='store_true');args=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',args.repo):raise ValueError('Use a simple repository name, not a URL')
    if not args.publish:
        print('DRY RUN: authenticate gh; restore/check local repo; update ppt-master main; run tests;')
        print(f'create a NEW PUBLIC {args.repo} in the authenticated personal account and push main.')
        print('No network write performed. Run with --publish only when ready.');return 0
    if not shutil.which('gh'):raise RuntimeError('Install GitHub CLI and run gh auth login locally; do not paste tokens into chat.')
    run(['gh','auth','status','--hostname','github.com'])
    user=json.loads(run(['gh','api','user']).stdout);login=user['login']
    if args.owner and args.owner!=login:raise RuntimeError('Requested owner is not the authenticated personal account')
    restore(ROOT)
    errors=check(ROOT)
    if errors:raise RuntimeError('Public-file check failed: '+'; '.join(errors))
    # Ensure no modified or untracked files get swept into the initial publication.
    if run(['git','status','--porcelain','--untracked-files=all']).stdout.strip():
        raise RuntimeError('Review and commit local changes before publication; no automatic git add .')
    fullname=f'{login}/{args.repo}'
    existing=run(['gh','api',f'repos/{fullname}'],check_return=False)
    if existing.returncode==0:raise RuntimeError('Repository already exists; refusing to overwrite or append to it.')
    if '404' not in existing.stderr:raise RuntimeError('Cannot safely determine whether the repository exists: '+existing.stderr.strip())
    if run(['git','remote']).stdout.strip():raise RuntimeError('Local repository has remotes; refusing ambiguous initial publication')
    record=update()
    if record['gitlink_commit_needed']:
        run(['git','add','--',SUB])
        # Public GitHub no-reply address, never the account's private email.
        author=f"{user['id']}+{login}@users.noreply.github.com"
        run(['git','-c',f'user.name={login}','-c',f'user.email={author}',
             'commit','-m','chore: follow current ppt-master main','--',SUB])
    tests=run([sys.executable,'-m','unittest','discover','-s','tests','-v'])
    print(tests.stdout,end='');print(tests.stderr,end='',file=sys.stderr)
    errors=check(ROOT)
    if errors:raise RuntimeError('; '.join(errors))
    print(f'Creating PUBLIC repository {fullname}; only reviewed tracked generic files will be pushed.')
    created=run(['gh','repo','create',fullname,'--public','--source',str(ROOT),'--remote','origin',
                 '--push','--description','Evidence-first research presentation skill: preparation, production handoff to ppt-master, and independent review/revision.'])
    print(created.stdout,end='')
    verified=json.loads(run(['gh','repo','view',fullname,'--json','url,visibility']).stdout)
    if verified.get('visibility')!='PUBLIC':raise RuntimeError('Creation returned but public visibility verification failed')
    remote_sha=run(['git','ls-remote','origin','refs/heads/main']).stdout.split()[0]
    local_sha=run(['git','rev-parse','HEAD']).stdout.strip()
    if remote_sha!=local_sha:raise RuntimeError('Remote main does not match the local publication commit')
    print(json.dumps({'status':'published','url':verified['url'],'commit':local_sha,'visibility':'PUBLIC'},indent=2))
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,RuntimeError,ValueError,subprocess.SubprocessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
