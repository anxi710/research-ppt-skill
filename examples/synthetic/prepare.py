#!/usr/bin/env python3
"""Create a synthetic preparation example; never claim this is actual paper evidence."""
import argparse
import sys
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
from helpers import workspace,w
from argparse import Namespace
import shutil

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if a.out.exists():raise SystemExit('Output already exists; choose a new path')
with tempfile.TemporaryDirectory() as t:
    project=workspace(Path(t),current_design=True);shutil.copytree(project,a.out)
w.handoff(Namespace(project=a.out,run_id='run-synthetic'))
print('Synthetic fixture only. Delegate PPT production to the current backend.')
