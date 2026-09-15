#!/usr/bin/env python3
"""Unit tests for deterministic, fail-closed finance calculations."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal, localcontext
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "skills/finance-core/finance-calculations/scripts/finance_cli.py"
spec = importlib.util.spec_from_file_location("finance_cli", MODULE)
finance = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(finance)

META = {
    "entity": "Synthetic Co",
    "period_start": "2026-01-01",
    "period_end": "2026-01-31",
    "as_of": "2026-02-01T09:00:00-05:00",
    "timezone": "America/New_York",
    "currency": "USD",
    "minor_units": 2,
    "accounting_basis": "accrual",
}


class MoneyTests(unittest.TestCase):
    def test_money_uses_decimal_exactly(self):
        self.assertEqual(finance.at_precision("0.1", 1) + finance.at_precision("0.2", 1), Decimal("0.3"))

    def test_float_money_is_rejected(self):
        with self.assertRaisesRegex(finance.ValidationError, "string or integer"):
            finance.at_precision(0.1, 2)

    def test_ambiguous_money_formats_are_rejected(self):
        for value in ("1e3", "1E+3", "1,000.00", "$12.00", " 12.00", "12.00 ", "+", ".5", "1.", True):
            with self.subTest(value=value), self.assertRaises(finance.ValidationError):
                finance.at_precision(value, 2)

    def test_currency_code_format_is_validated_without_claiming_iso_membership(self):
        with self.assertRaisesRegex(finance.ValidationError, "currency code"):
            finance.validate_context({**META, "currency": "dollars"})

    def test_missing_precision_is_rejected_as_ambiguous(self):
        ctx = {k: v for k, v in META.items() if k != "minor_units"}
        with self.assertRaisesRegex(finance.ValidationError, "minor_units"):
            finance.validate_context(ctx)

    def test_non_finite_money_is_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), self.assertRaisesRegex(finance.ValidationError, "finite"):
                finance.at_precision(value, 2)

    def test_missing_is_not_zero(self):
        with self.assertRaisesRegex(finance.ValidationError, "missing required"):
            finance.sum_money([{"amount": "1.00"}, {}], "amount", minor_units=2)

    def test_mixed_currency_is_rejected_without_fx(self):
        rows = [{"amount": "1", "currency": "USD"}, {"amount": "2", "currency": "CAD"}]
        with self.assertRaisesRegex(finance.ValidationError, "currency"):
            finance.sum_money(rows, "amount", expected_currency="USD", minor_units=2)

    def test_oversized_decimal_is_rejected_structurally(self):
        with self.assertRaisesRegex(finance.ValidationError, "digits"):
            finance.at_precision("1" * 1001, 2)

    def test_negative_zero_is_normalized(self):
        self.assertEqual(finance.format_money("-0.00", 2), "0.00")


class ExactArithmeticTests(unittest.TestCase):
    def test_sum_preserves_carry_growth(self):
        rows = [{"amount": "9" * 40 + ".99"}, {"amount": "0.01"}]
        self.assertEqual(finance.sum_money(rows, "amount", 2),
                         Decimal("1" + "0" * 40 + ".00"))

    def test_sum_preserves_mixed_sign_cancellation(self):
        magnitude = "1" + "0" * 40
        rows = [{"amount": magnitude + ".01"}, {"amount": "-" + magnitude + ".00"}]
        self.assertEqual(finance.sum_money(rows, "amount", 2), Decimal("0.01"))

    def test_forecast_net_flow_preserves_large_cancellation(self):
        magnitude = "1" + "0" * 40
        weeks = [{"week": i + 1,
                  "week_start": (date(2026, 1, 5) + timedelta(weeks=i)).isoformat(),
                  "receipts": magnitude + ".01",
                  "disbursements": magnitude + ".00"} for i in range(13)]
        result = finance.cash_forecast("0.00", weeks, "USD", 2)
        self.assertTrue(all(row["net_cash_flow"] == "0.01" for row in result))
        self.assertEqual(result[-1]["closing_cash"], "0.13")

    def test_sum_preserves_cents_beyond_default_decimal_precision(self):
        amount = "1" + "0" * 35 + ".01"
        rows = [{"amount": amount}, {"amount": "0.01"}]
        self.assertEqual(finance.sum_money(rows, "amount", 2),
                         Decimal("1" + "0" * 35 + ".02"))

    def test_variance_does_not_inherit_callers_precision(self):
        with localcontext() as ctx:
            ctx.prec = 4
            result = finance.budget_variance("1000000.01", "0.00", "expense", 2)
        self.assertEqual(result["raw_variance_actual_minus_budget"], "-1000000.01")
        self.assertEqual(result["favorable_variance"], "1000000.01")

    def test_balance_equation_preserves_large_small_differences(self):
        integer = "1" + "0" * 35
        result = finance.balance_sheet_check(integer + ".01", "0.00", integer, 2)
        self.assertEqual(result, {"difference": "0.01", "status": "unbalanced"})

    def test_forecast_preserves_cents_with_large_opening_balance(self):
        integer = "1" + "0" * 35
        weeks = [{"week": i + 1,
                  "week_start": (date(2026, 1, 5) + timedelta(weeks=i)).isoformat(),
                  "receipts": "0.01", "disbursements": "0.00"} for i in range(13)]
        result = finance.cash_forecast(integer + ".00", weeks, "USD", 2)
        self.assertEqual(result[-1]["closing_cash"], integer + ".13")


class ContextTests(unittest.TestCase):
    def test_missing_entity_is_rejected(self):
        ctx = {k: v for k, v in META.items() if k != "entity"}
        with self.assertRaisesRegex(finance.ValidationError, "entity"):
            finance.validate_context(ctx)

    def test_invalid_period_order_is_rejected(self):
        with self.assertRaisesRegex(finance.ValidationError, "period_start"):
            finance.validate_context({**META, "period_start": "2026-02-01"})

    def test_invalid_basis_is_rejected(self):
        with self.assertRaisesRegex(finance.ValidationError, "accounting_basis"):
            finance.validate_context({**META, "accounting_basis": "mixed"})

    def test_as_of_requires_timezone_offset(self):
        with self.assertRaisesRegex(finance.ValidationError, "offset"):
            finance.validate_context({**META, "as_of": "2026-02-01T09:00:00"})

    def test_timezone_must_be_valid_and_match_as_of_offset(self):
        with self.assertRaisesRegex(finance.ValidationError, "timezone"):
            finance.validate_context({**META, "timezone": "Mars/Olympus"})
        with self.assertRaisesRegex(finance.ValidationError, "does not match"):
            finance.validate_context({**META, "as_of": "2026-02-01T09:00:00+09:00"})


class CalculationTests(unittest.TestCase):
    def test_rate_returns_numerator_denominator_and_precision_policy(self):
        self.assertEqual(finance.rate("1", "3", 4, "ROUND_HALF_EVEN"), {"numerator": "1", "denominator": "3", "rate": "0.3333", "precision": 4, "rounding_method": "ROUND_HALF_EVEN"})

    def test_rate_zero_denominator_is_unknown(self):
        self.assertEqual(finance.rate("0", "0", 4, "ROUND_HALF_EVEN"), {"numerator": "0", "denominator": "0", "rate": None, "status": "undefined", "precision": 4, "rounding_method": "ROUND_HALF_EVEN"})

    def forecast_weeks(self, receipts="10.00", disbursements="4.00"):
        start = date(2026, 2, 2)
        return [
            {"week": i, "week_start": (start + timedelta(days=7 * (i - 1))).isoformat(), "receipts": receipts, "disbursements": disbursements}
            for i in range(1, 14)
        ]

    def test_forecast_rolls_thirteen_weeks(self):
        weeks = self.forecast_weeks()
        out = finance.cash_forecast("100.00", weeks, "USD", 2)
        self.assertEqual(len(out), 13)
        self.assertEqual(out[0]["opening_cash"], "100.00")
        self.assertEqual(out[0]["closing_cash"], "106.00")
        self.assertEqual(out[-1]["closing_cash"], "178.00")
        self.assertEqual(out[0]["week_start"], "2026-02-02")
        self.assertEqual(out[-1]["week_start"], "2026-04-27")

    def test_forecast_rejects_wrong_week_count(self):
        with self.assertRaisesRegex(finance.ValidationError, "exactly 13"):
            finance.cash_forecast("100", [], "USD", 2)

    def test_forecast_rejects_roll_forward_break(self):
        weeks = self.forecast_weeks()
        weeks[1]["opening_cash"] = "999"
        with self.assertRaisesRegex(finance.ValidationError, "roll-forward"):
            finance.cash_forecast("100", weeks, "USD", 2)

    def test_forecast_uses_owner_confirmed_three_decimal_precision(self):
        weeks = self.forecast_weeks("0.001", "0.000")
        out = finance.cash_forecast("1.000", weeks, "BHD", 3)
        self.assertEqual(out[0]["closing_cash"], "1.001")
        self.assertEqual(out[-1]["closing_cash"], "1.013")

    def test_forecast_rejects_amount_beyond_confirmed_precision(self):
        weeks = self.forecast_weeks("0.001", "0.00")
        with self.assertRaisesRegex(finance.ValidationError, "minor_units"):
            finance.cash_forecast("1.00", weeks, "USD", 2)

    def test_forecast_rejects_nonconsecutive_or_invalid_week_start(self):
        for bad in ("2026-02-10", "not-a-date"):
            weeks = self.forecast_weeks()
            weeks[1]["week_start"] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(finance.ValidationError, "week_start"):
                finance.cash_forecast("100.00", weeks, "USD", 2)

    def test_forecast_rejects_boolean_week_number(self):
        weeks = self.forecast_weeks()
        weeks[0]["week"] = True
        with self.assertRaisesRegex(finance.ValidationError, "week"):
            finance.cash_forecast("100.00", weeks, "USD", 2)

    def test_runway_zero_burn_is_not_infinite_number(self):
        self.assertEqual(finance.runway("100", "0", 2, 2, "ROUND_HALF_EVEN"), {"months": None, "status": "no_current_burn", "precision": 2, "rounding_method": "ROUND_HALF_EVEN"})

    def test_runway_negative_cash_is_exhausted(self):
        self.assertEqual(finance.runway("-1", "10", 2, 2, "ROUND_HALF_EVEN"), {"months": "0.00", "status": "cash_exhausted", "precision": 2, "rounding_method": "ROUND_HALF_EVEN"})

    def test_runway_nonterminating_division_is_quantized_explicitly(self):
        self.assertEqual(finance.runway("100", "30", 2, 2, "ROUND_HALF_EVEN")["months"], "3.33")

    def test_budget_variance_expense_favorable_sign(self):
        self.assertEqual(finance.budget_variance("100", "90", "expense", 2)["favorable_variance"], "10.00")

    def test_budget_variance_revenue_favorable_sign(self):
        self.assertEqual(finance.budget_variance("100", "110", "revenue", 2)["favorable_variance"], "10.00")

    def test_ar_aging_boundaries(self):
        self.assertEqual(finance.ar_bucket(0), "current")
        self.assertEqual(finance.ar_bucket(1), "1-30")
        self.assertEqual(finance.ar_bucket(30), "1-30")
        self.assertEqual(finance.ar_bucket(31), "31-60")
        self.assertEqual(finance.ar_bucket(60), "31-60")
        self.assertEqual(finance.ar_bucket(61), "61-90")
        self.assertEqual(finance.ar_bucket(90), "61-90")
        self.assertEqual(finance.ar_bucket(91), "90+")

    def test_balance_sheet_equation_is_balanced_not_reconciled(self):
        self.assertEqual(finance.balance_sheet_check("100.00", "40", "60", 2), {"difference": "0.00", "status": "balanced"})
        self.assertEqual(finance.balance_sheet_check("100.00", "39", "60", 2), {"difference": "1.00", "status": "unbalanced"})

    def test_duplicates_are_detected(self):
        rows = [{"id": "a", "amount": "1"}, {"id": "a", "amount": "1"}, {"id": "b", "amount": "2"}]
        self.assertEqual(finance.duplicate_keys(rows, ["id", "amount"]), [{"key": ["a", "1"], "row_indexes": [0, 1]}])

    def test_reconciliation_status_requires_evidence(self):
        self.assertEqual(finance.reconciliation_status("0", True, True, 2), "reconciled")
        self.assertEqual(finance.reconciliation_status("0", False, True, 2), "not_tested")
        self.assertEqual(finance.reconciliation_status("1", True, True, 2), "unreconciled")


class CliTests(unittest.TestCase):
    def test_cli_json_round_trip(self):
        payload = {"operation": "balance_sheet", "context": META, "inputs": {"assets": "100", "liabilities": "40", "equity": "60"}}
        proc = subprocess.run([sys.executable, str(MODULE)], input=json.dumps(payload), text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["result"]["status"], "balanced")
        self.assertEqual(result["context"]["entity"], "Synthetic Co")

    def test_cli_fails_closed_on_unknown_fields(self):
        payload = {"operation": "balance_sheet", "context": META, "inputs": {"assets": "100", "liabilities": "40", "equity": "60", "guess": True}}
        proc = subprocess.run([sys.executable, str(MODULE)], input=json.dumps(payload), text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown field", json.loads(proc.stderr)["error"])

    def test_cli_rejects_money_beyond_declared_minor_units_without_rounding(self):
        payload = {"operation": "balance_sheet", "context": META, "inputs": {"assets": "100.001", "liabilities": "40.00", "equity": "60.00"}}
        proc = subprocess.run([sys.executable, str(MODULE)], input=json.dumps(payload), text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2)
        error = json.loads(proc.stderr)["error"]
        self.assertIn("minor_units", error)
        self.assertNotIn("rounded", error.lower())

    def test_cli_rejects_duplicate_json_members(self):
        raw = '{"operation":"balance_sheet","operation":"rate","context":{},"inputs":{}}'
        proc = subprocess.run([sys.executable, str(MODULE)], input=raw, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("duplicate JSON member", json.loads(proc.stderr)["error"])

    def test_cli_rejects_json_nan_and_infinity_constants(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            raw = '{"operation":"balance_sheet","context":{},"inputs":{"assets":'+constant+'}}'
            proc = subprocess.run([sys.executable, str(MODULE)], input=raw, text=True, capture_output=True)
            with self.subTest(constant=constant):
                self.assertEqual(proc.returncode, 2)
                self.assertIn("non-standard JSON constant", json.loads(proc.stderr)["error"])

    def test_json_output_forbids_nan(self):
        with self.assertRaises(ValueError):
            finance.strict_dumps({"bad": float("nan")})

    def test_cli_reports_undefined_rate(self):
        payload = {"operation":"rate","context":META,"inputs":{"numerator":"0","denominator":"0","precision":4,"rounding_method":"ROUND_HALF_EVEN"}}
        proc = subprocess.run([sys.executable,str(MODULE)],input=json.dumps(payload),text=True,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["result"]["status"],"undefined")

    def test_cli_reports_reconciliation_not_tested_without_control_evidence(self):
        payload = {"operation":"reconciliation_status","context":META,"inputs":{"difference":"0.00","source_complete":False,"controls_tested":True}}
        proc = subprocess.run([sys.executable,str(MODULE)],input=json.dumps(payload),text=True,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["result"]["status"],"not_tested")


if __name__ == "__main__":
    unittest.main(verbosity=2)
