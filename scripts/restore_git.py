#!/usr/bin/env python3
"""Restore the local Git history from the offline package's bundle; no network writes."""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def restore(root: Path=ROOT) -> None:
    if (root/'.git').exists():
        print('Git metadata already present; no restore performed.');return
    bundle=root/'research-ppt-skill.bundle'
    if not bundle.is_file():raise RuntimeError('No Git metadata/bundle. Clone the published repository instead.')
    probe=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=root,capture_output=True,text=True)
    if probe.returncode==0:raise RuntimeError('Extract outside another Git repository before restoring.')
    def run(*args):subprocess.run(['git',*args],cwd=root,check=True,timeout=60)
    run('init','--initial-branch=main')
    run('bundle','verify',str(bundle))
    run('fetch',str(bundle),'refs/heads/main:refs/heads/main')
    # Reset only the index. Existing working files are never overwritten.
    run('reset','--mixed','HEAD')
    print('Restored main and its real submodule gitlink; upstream bytes are not bundled.')

if __name__=='__main__':
    try:restore()
    except (RuntimeError,OSError,subprocess.SubprocessError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);raise SystemExit(2)
