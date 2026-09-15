#!/usr/bin/env python3
"""Deterministic finance calculations with strict JSON input/output.

This tool performs local arithmetic only. It has no network, credential, file
write, or external-system code path. Monetary inputs must be JSON strings or
integers; floats are rejected before Decimal conversion.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, localcontext, ROUND_HALF_EVEN
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
PLAIN_DECIMAL_RE = re.compile(r"^[+-]?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
BASES = {"cash", "accrual"}
MAX_DECIMAL_DIGITS = 1000
ROUNDING_METHODS = {"ROUND_HALF_EVEN": ROUND_HALF_EVEN}


class ValidationError(ValueError):
    """Input is missing, ambiguous, or invalid."""


def _money(value: Any) -> Decimal:
    """Parse a money token internally; callers must also enforce minor_units."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValidationError("money must be supplied as a plain decimal string or integer; JSON floats are rejected")
    raw = str(value)
    if raw in {"NaN", "+NaN", "-NaN", "Infinity", "+Infinity", "-Infinity"}:
        raise ValidationError("money must be finite")
    if not PLAIN_DECIMAL_RE.fullmatch(raw):
        raise ValidationError("money must use plain signed decimal notation without exponent, separators, symbols, or surrounding whitespace")
    digits = raw.lstrip("+-").replace(".", "")
    if len(digits) > MAX_DECIMAL_DIGITS:
        raise ValidationError(f"money exceeds the {MAX_DECIMAL_DIGITS}-digits safety limit")
    try:
        result = Decimal(raw)
    except InvalidOperation as exc:
        raise ValidationError(f"invalid decimal amount: {value!r}") from exc
    if not result.is_finite():
        raise ValidationError("money must be finite")
    return result


def at_precision(value: Any, minor_units: int) -> Decimal:
    if isinstance(minor_units, bool) or not isinstance(minor_units, int) or not 0 <= minor_units <= 9:
        raise ValidationError("minor_units must be an owner-confirmed integer from 0 through 9")
    amount = _money(value)
    exponent = amount.as_tuple().exponent
    fractional_places = max(0, -int(exponent))
    if fractional_places > minor_units:
        raise ValidationError(f"amount {value!r} exceeds owner-confirmed minor_units={minor_units}")
    return amount


def _quantized(value: Decimal, places: int, rounding_method: str) -> Decimal:
    if isinstance(places, bool) or not isinstance(places, int) or not 0 <= places <= 12:
        raise ValidationError("precision must be an explicit integer from 0 through 12")
    if rounding_method not in ROUNDING_METHODS:
        raise ValidationError("rounding_method must be ROUND_HALF_EVEN")
    with localcontext() as ctx:
        ctx.prec = max(MAX_DECIMAL_DIGITS + places + 5, len(value.as_tuple().digits) + places + 5)
        try:
            return value.quantize(Decimal(1).scaleb(-places), rounding=ROUNDING_METHODS[rounding_method])
        except InvalidOperation as exc:
            raise ValidationError("decimal result cannot be represented at the requested precision") from exc


def format_money(value: Any, minor_units: int) -> str:
    return fmt(at_precision(value, minor_units), minor_units)


def number(value: Any) -> Decimal:
    return _money(value)


def fmt(value: Decimal, places: int | None = None) -> str:
    if value == 0:
        value = value.copy_abs()
    if places is not None:
        quantum = Decimal(1).scaleb(-places)
        with localcontext() as ctx:
            ctx.prec = max(MAX_DECIMAL_DIGITS + places + 5, len(value.as_tuple().digits) + places + 5)
            return format(value.quantize(quantum), f".{places}f")
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _require_keys(data: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(data))
    if missing:
        raise ValidationError(f"{label} missing required field(s): {', '.join(missing)}")


def _exact_keys(data: dict[str, Any], required: set[str], optional: set[str] | None = None, label: str = "object") -> None:
    optional = optional or set()
    _require_keys(data, required, label)
    unknown = sorted(set(data) - required - optional)
    if unknown:
        raise ValidationError(f"{label} has unknown field(s): {', '.join(unknown)}")


def validate_context(context: dict[str, Any]) -> dict[str, Any]:
    required = {"entity", "period_start", "period_end", "as_of", "timezone", "currency", "minor_units", "accounting_basis"}
    _exact_keys(context, required, label="context")
    for field in ("entity", "timezone"):
        if not isinstance(context[field], str) or not context[field].strip():
            raise ValidationError(f"context {field} must be a non-empty string")
    try:
        start = date.fromisoformat(context["period_start"])
        end = date.fromisoformat(context["period_end"])
    except (TypeError, ValueError) as exc:
        raise ValidationError("period_start and period_end must be ISO dates") from exc
    if start > end:
        raise ValidationError("period_start must be on or before period_end")
    try:
        as_of = datetime.fromisoformat(context["as_of"])
    except (TypeError, ValueError) as exc:
        raise ValidationError("as_of must be an ISO timestamp") from exc
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValidationError("as_of must include a UTC offset")
    try:
        zone = ZoneInfo(context["timezone"])
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValidationError("context timezone must be a valid IANA timezone label") from exc
    if as_of.astimezone(zone).utcoffset() != as_of.utcoffset():
        raise ValidationError("as_of UTC offset does not match context timezone at that instant")
    currency = context["currency"]
    if not isinstance(currency, str) or not CURRENCY_RE.fullmatch(currency):
        raise ValidationError("currency code must be exactly three uppercase letters; this format check does not prove ISO 4217 membership")
    minor_units = context["minor_units"]
    if isinstance(minor_units, bool) or not isinstance(minor_units, int) or not 0 <= minor_units <= 9:
        raise ValidationError("minor_units must be an owner-confirmed integer from 0 through 9")
    if context["accounting_basis"] not in BASES:
        raise ValidationError("accounting_basis must be cash or accrual")
    return dict(context)


def _sum_exact(values: list[Decimal]) -> Decimal:
    """Reserve all integral/fractional digits plus carry space for the sum."""
    integral = max((max(value.adjusted() + 1, 0) for value in values), default=1)
    fractional = max((max(-int(value.as_tuple().exponent), 0) for value in values), default=0)
    with localcontext() as ctx:
        ctx.prec = integral + fractional + len(str(len(values))) + 1
        return sum(values, Decimal("0"))


def sum_money(rows: list[dict[str, Any]], field: str, minor_units: int, expected_currency: str | None = None) -> Decimal:
    values = []
    for index, row in enumerate(rows):
        if field not in row or row[field] is None:
            raise ValidationError(f"row {index} missing required {field}; missing is not zero")
        if expected_currency is not None and row.get("currency") != expected_currency:
            raise ValidationError(f"row {index} currency does not match {expected_currency}; provide an explicit dated FX method")
        values.append(at_precision(row[field], minor_units))
    return _sum_exact(values)


def rate(numerator: Any, denominator: Any, precision: int, rounding_method: str) -> dict[str, Any]:
    n, d = number(numerator), number(denominator)
    policy = {"precision": precision, "rounding_method": rounding_method}
    _quantized(Decimal("0"), precision, rounding_method)
    if d == 0:
        return {"numerator": fmt(n), "denominator": fmt(d), "rate": None, "status": "undefined", **policy}
    with localcontext() as ctx:
        ctx.prec = MAX_DECIMAL_DIGITS + precision + 10
        result = _quantized(n / d, precision, rounding_method)
    return {"numerator": fmt(n), "denominator": fmt(d), "rate": fmt(result, precision), **policy}


def cash_forecast(opening_cash: Any, weeks: list[dict[str, Any]], currency: str, minor_units: int) -> list[dict[str, Any]]:
    if not CURRENCY_RE.fullmatch(currency or ""):
        raise ValidationError("currency code must be exactly three uppercase letters")
    if isinstance(minor_units, bool) or not isinstance(minor_units, int) or not 0 <= minor_units <= 9:
        raise ValidationError("minor_units must be an owner-confirmed integer from 0 through 9")
    if len(weeks) != 13:
        raise ValidationError("cash forecast requires exactly 13 weekly rows")
    opening = at_precision(opening_cash, minor_units)
    output: list[dict[str, Any]] = []
    prior_week_start: date | None = None
    for expected_week, row in enumerate(weeks, 1):
        _exact_keys(row, {"week", "week_start", "receipts", "disbursements"}, {"opening_cash"}, f"week {expected_week}")
        if isinstance(row["week"], bool) or not isinstance(row["week"], int) or row["week"] != expected_week:
            raise ValidationError(f"week sequence must use integer values 1 through 13; expected {expected_week}")
        try:
            week_start = date.fromisoformat(row["week_start"])
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"week {expected_week} week_start must be an ISO date") from exc
        if prior_week_start is not None and (week_start - prior_week_start).days != 7:
            raise ValidationError(f"week {expected_week} week_start must be exactly 7 days after the prior week")
        if "opening_cash" in row and at_precision(row["opening_cash"], minor_units) != opening:
            raise ValidationError(f"week {expected_week} opening_cash breaks roll-forward")
        receipts = at_precision(row["receipts"], minor_units)
        disbursements = at_precision(row["disbursements"], minor_units)
        closing = _sum_exact([opening, receipts, disbursements.copy_negate()])
        output.append({
            "week": expected_week,
            "week_start": week_start.isoformat(),
            "currency": currency,
            "minor_units": minor_units,
            "opening_cash": fmt(opening, minor_units),
            "receipts": fmt(receipts, minor_units),
            "disbursements": fmt(disbursements, minor_units),
            "net_cash_flow": fmt(_sum_exact([receipts, disbursements.copy_negate()]), minor_units),
            "closing_cash": fmt(closing, minor_units),
        })
        opening = closing
        prior_week_start = week_start
    return output


def runway(unrestricted_cash: Any, monthly_net_burn: Any, minor_units: int, precision: int, rounding_method: str) -> dict[str, Any]:
    cash, burn = at_precision(unrestricted_cash, minor_units), at_precision(monthly_net_burn, minor_units)
    policy = {"precision": precision, "rounding_method": rounding_method}
    zero = fmt(_quantized(Decimal("0"), precision, rounding_method), precision)
    if cash <= 0:
        return {"months": zero, "status": "cash_exhausted", **policy}
    if burn <= 0:
        return {"months": None, "status": "no_current_burn", **policy}
    with localcontext() as ctx:
        ctx.prec = MAX_DECIMAL_DIGITS + precision + 10
        months = _quantized(cash / burn, precision, rounding_method)
    return {"months": fmt(months, precision), "status": "calculated", **policy}


def budget_variance(budget: Any, actual: Any, account_type: str, minor_units: int) -> dict[str, str]:
    if account_type not in {"revenue", "expense"}:
        raise ValidationError("account_type must be revenue or expense; classification may not be inferred")
    b, a = at_precision(budget, minor_units), at_precision(actual, minor_units)
    raw = _sum_exact([a, b.copy_negate()])
    favorable = raw if account_type == "revenue" else raw.copy_negate()
    return {"budget": fmt(b, minor_units), "actual": fmt(a, minor_units), "raw_variance_actual_minus_budget": fmt(raw, minor_units), "favorable_variance": fmt(favorable, minor_units)}


def ar_bucket(days_past_due: int) -> str:
    if isinstance(days_past_due, bool) or not isinstance(days_past_due, int):
        raise ValidationError("days_past_due must be an integer")
    if days_past_due <= 0:
        return "current"
    if days_past_due <= 30:
        return "1-30"
    if days_past_due <= 60:
        return "31-60"
    if days_past_due <= 90:
        return "61-90"
    return "90+"


def balance_sheet_check(assets: Any, liabilities: Any, equity: Any, minor_units: int) -> dict[str, str]:
    difference = _sum_exact([
        at_precision(assets, minor_units),
        at_precision(liabilities, minor_units).copy_negate(),
        at_precision(equity, minor_units).copy_negate(),
    ])
    return {"difference": fmt(difference, minor_units), "status": "balanced" if difference == 0 else "unbalanced"}


def duplicate_keys(rows: list[dict[str, Any]], key_fields: list[str]) -> list[dict[str, Any]]:
    if not key_fields:
        raise ValidationError("at least one duplicate key field is required")
    seen: dict[tuple[Any, ...], list[int]] = {}
    for index, row in enumerate(rows):
        missing = [key for key in key_fields if key not in row or row[key] is None]
        if missing:
            raise ValidationError(f"row {index} missing duplicate key field(s): {', '.join(missing)}")
        key = tuple(row[field] for field in key_fields)
        seen.setdefault(key, []).append(index)
    return [{"key": list(key), "row_indexes": indexes} for key, indexes in seen.items() if len(indexes) > 1]


def reconciliation_status(difference: Any, source_complete: bool, controls_tested: bool, minor_units: int) -> str:
    if not isinstance(source_complete, bool) or not isinstance(controls_tested, bool):
        raise ValidationError("source_complete and controls_tested must be booleans")
    if not source_complete or not controls_tested:
        return "not_tested"
    return "reconciled" if at_precision(difference, minor_units) == 0 else "unreconciled"


OPERATIONS: dict[str, tuple[set[str], Any]] = {
    "balance_sheet": ({"assets", "liabilities", "equity"}, lambda x, c: balance_sheet_check(x["assets"], x["liabilities"], x["equity"], c["minor_units"])),
    "budget_variance": ({"budget", "actual", "account_type"}, lambda x, c: budget_variance(x["budget"], x["actual"], x["account_type"], c["minor_units"])),
    "cash_forecast": ({"opening_cash", "weeks"}, lambda x, c: cash_forecast(x["opening_cash"], x["weeks"], c["currency"], c["minor_units"])),
    "rate": ({"numerator", "denominator", "precision", "rounding_method"}, lambda x, c: rate(x["numerator"], x["denominator"], x["precision"], x["rounding_method"])),
    "runway": ({"unrestricted_cash", "monthly_net_burn", "precision", "rounding_method"}, lambda x, c: runway(x["unrestricted_cash"], x["monthly_net_burn"], c["minor_units"], x["precision"], x["rounding_method"])),
    "ar_bucket": ({"days_past_due"}, lambda x, c: {"bucket": ar_bucket(x["days_past_due"])}),
    "duplicates": ({"rows", "key_fields"}, lambda x, c: {"duplicates": duplicate_keys(x["rows"], x["key_fields"])}),
    "reconciliation_status": ({"difference", "source_complete", "controls_tested"}, lambda x, c: {"status": reconciliation_status(x["difference"], x["source_complete"], x["controls_tested"], c["minor_units"])}),
}


def execute(payload: dict[str, Any]) -> dict[str, Any]:
    _exact_keys(payload, {"operation", "context", "inputs"}, label="request")
    operation = payload["operation"]
    if operation not in OPERATIONS:
        raise ValidationError(f"unsupported operation: {operation!r}")
    if not isinstance(payload["context"], dict) or not isinstance(payload["inputs"], dict):
        raise ValidationError("context and inputs must be objects")
    context = validate_context(payload["context"])
    fields, function = OPERATIONS[operation]
    _exact_keys(payload["inputs"], fields, label="inputs")
    return {"operation": operation, "context": context, "result": function(payload["inputs"], context), "calculation_status": "calculated"}


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise ValidationError(f"non-standard JSON constant is forbidden: {value}")


def _reject_float(raw: str) -> Any:
    raise ValidationError(f"JSON float {raw} is forbidden; use a plain decimal string")


def strict_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    try:
        payload = json.load(sys.stdin, parse_float=_reject_float, parse_constant=_reject_constant, object_pairs_hook=_object_no_duplicates)
        if not isinstance(payload, dict):
            raise ValidationError("request must be a JSON object")
        print(strict_dumps(execute(payload)))
        return 0
    except (json.JSONDecodeError, ValidationError, TypeError) as exc:
        print(strict_dumps({"error": str(exc), "status": "rejected"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
