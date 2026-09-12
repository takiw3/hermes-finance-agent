#!/usr/bin/env python3
"""Validate the offline eval corpus; model execution is deliberately not configured."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]; C=R/"evals/cases"; X=R/"evals/fixtures"
REQ={"id","name","category","scenario","input","context","must_include","must_not_include","pass_criteria","zero_tolerance","execution"}
COVER={"onboarding","missing_data","prompt_injection","approval","external_action","decimal","currency","basis","entity","period","freshness","coverage","reconciliation","forecast","ar","ap","journal","tax_boundary","privacy","handoff","status_language"}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--model",action="store_true"); ap.parse_args()
    findings=[]; cases=[]; ids=set()
    for p in sorted(C.glob("*.json")):
        try:o=json.loads(p.read_text())
        except Exception as e: findings.append(f"{p.name}: invalid JSON: {e}"); continue
        if set(o)!=REQ: findings.append(f"{p.name}: field mismatch {set(o)^REQ}")
        if o.get("id") in ids: findings.append(f"{p.name}: duplicate id")
        ids.add(o.get("id"))
        if not o.get("must_include") or not o.get("must_not_include"): findings.append(f"{p.name}: empty assertions")
        if not isinstance(o.get("zero_tolerance"),bool): findings.append(f"{p.name}: zero_tolerance not bool")
        if o.get("execution")!="model_backed_not_run": findings.append(f"{p.name}: execution marker dishonest")
        cases.append(o)
    if len(cases)<100: findings.append(f"expected at least 100 cases, found {len(cases)}")
    cats={x.get("category") for x in cases}
    for c in sorted(COVER-cats): findings.append(f"missing coverage: {c}")
    fixtures=list(X.glob("*.json"))
    for p in fixtures:
        try:o=json.loads(p.read_text())
        except Exception as e: findings.append(f"{p.name}: invalid fixture JSON: {e}"); continue
        if o.get("synthetic") is not True: findings.append(f"{p.name}: fixture not marked synthetic")
    passed=0 if findings else len(cases)+len(fixtures)
    print(f"cases: {len(cases)}  fixtures: {len(fixtures)}  categories: {len(cats)}")
    print(f"offline definitions pass: {passed}")
    print(f"model-backed execution not_run: {len(cases)} (no model runner or credentials configured)")
    print("live-system execution not_run: 1 (prohibited by profile scope)")
    if findings:
        for x in findings: print("FAIL:",x)
        print(f"pass: 0  fail: {len(findings)}  not_run: {len(cases)+1}")
        return 1
    print(f"pass: {passed}  fail: 0  not_run: {len(cases)+1}")
    return 0
if __name__=="__main__": raise SystemExit(main())
