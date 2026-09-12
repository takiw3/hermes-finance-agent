#!/usr/bin/env python3
from __future__ import annotations
import json, re, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[2]
class SkillContracts(unittest.TestCase):
    def setUp(self): self.skills=sorted((R/"skills/finance-core").glob("*/SKILL.md"))
    def test_exact_skill_count(self): self.assertEqual(len(self.skills),29)
    def test_every_skill_has_operational_contract(self):
        sections=["## Inputs","## Procedure","## Output contract","## When not to use","## Source handling","## Refusal and escalation","## Failure behavior","## Verification checklist"]
        for p in self.skills:
            b=p.read_text()
            with self.subTest(skill=p.parent.name):
                self.assertRegex(b,r"(?m)^description: \"Use when ")
                for s in sections:self.assertIn(s,b)
                self.assertIn("Missing/unavailable is never zero",b)
                self.assertIn("No raw finance data",b)
    def test_procedures_are_distinct(self):
        procedures=[]
        for p in self.skills:
            b=p.read_text(); procedures.append(b.split("## Procedure",1)[1].split("## Output contract",1)[0])
        self.assertEqual(len(procedures),len(set(procedures)))
    def test_artifact_pairs_exist(self):
        schemas={p.name.replace(".schema.json","") for p in (R/"schemas").glob("*.schema.json")}
        templates={p.name.replace(".template.json","") for p in (R/"templates").glob("*.template.json")}
        self.assertEqual(schemas,templates)
        self.assertEqual(len(schemas),11)
    def test_schemas_fail_closed(self):
        for p in (R/"schemas").glob("*.json"):
            with self.subTest(schema=p.name): self.assertIs(json.loads(p.read_text()).get("additionalProperties"),False)
    def test_correctness_metadata_present_in_report_schemas(self):
        fields={"entity","period_start","period_end","as_of","timezone","currency","minor_units","accounting_basis","sources","source_coverage","freshness","reconciliation_status"}
        for name in ["management-report","cash-forecast","budget-variance","ar-ap-plan","scenario","reconciliation-result"]:
            o=json.loads((R/f"schemas/{name}.schema.json").read_text())
            with self.subTest(schema=name): self.assertTrue(fields<=set(o["required"]))
    def test_source_registries_are_empty(self):
        for p in (R/"references").glob("*.json"):
            o=json.loads(p.read_text())
            with self.subTest(registry=p.name): self.assertFalse(any(v for v in o.values() if isinstance(v,list)))
if __name__=="__main__": unittest.main(verbosity=2)
