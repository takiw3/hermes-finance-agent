#!/usr/bin/env python3
"""Honest local Hermes compatibility report; no network/tag downloads."""
from __future__ import annotations
import os, re, subprocess, sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def main():
    passed=failed=not_run=0
    try:p=subprocess.run(["hermes","--version"],capture_output=True,text=True,timeout=30)
    except (FileNotFoundError,subprocess.TimeoutExpired):
        print("not_run: local Hermes version (binary unavailable)"); print("not_run: actual approvals.deny matcher (no public offline harness)"); print("pass: 0  fail: 0  not_run: 2"); return 0
    out=(p.stdout+p.stderr).strip(); m=re.search(r"(\d+)\.(\d+)\.(\d+)",out)
    if p.returncode or not m:
        print(f"not_run: local Hermes version could not be parsed: {out}"); not_run+=1
    else:
        v=tuple(map(int,m.groups()))
        if v>=(0,20,0): print(f"ok: local Hermes {'.'.join(m.groups())} meets >=0.20.0"); passed+=1
        else: print(f"FAIL: local Hermes {'.'.join(m.groups())} is below >=0.20.0"); failed+=1
    checkout=os.environ.get("HERMES_CHECKOUT")
    if checkout and Path(checkout).resolve().is_relative_to(R.resolve()):
        print("not_run: release-tag matrix (no in-repository Hermes checkout fixture)"); not_run+=1
    else:
        print("not_run: release-tag matrix (network disabled; set an in-repository reviewed fixture to extend)"); not_run+=1
    print("not_run: actual approvals.deny matcher (Hermes exposes no stable noninteractive matcher CLI; fnmatch simulation is intentionally not counted)"); not_run+=1
    print(f"pass: {passed}  fail: {failed}  not_run: {not_run}")
    return 1 if failed else 0
if __name__=="__main__": raise SystemExit(main())
