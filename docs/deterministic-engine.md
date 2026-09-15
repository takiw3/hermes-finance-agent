# Deterministic engine

## Invocation

```bash
python3 skills/finance-core/finance-calculations/scripts/finance_cli.py < request.json
```

The engine reads one JSON object and writes compact JSON. Success exits `0` on stdout. Validation rejection exits `2` with `{status:"rejected", error:"..."}` on stderr. It performs no network, subprocess, credential, file-read, or file-write operation.

## Request contract

Top-level fields are exactly `operation`, `context`, and `inputs`. Context is exact and requires entity, ISO period dates, offset-aware `as_of`, valid IANA timezone, three-uppercase-letter currency code, owner-confirmed `minor_units` from 0-9, and `cash` or `accrual` basis. ZoneInfo cross-validates the timestamp offset against the timezone at that instant. The currency format check does not prove ISO 4217 membership.

JSON duplicate members, JSON floats, NaN/Infinity constants, unknown fields, and wrong types are rejected. Money accepts plain signed decimal strings or integers only. Exponent notation, separators, symbols, surrounding whitespace, booleans, non-finite values, more than 1000 digits, and precision beyond `minor_units` are rejected. Negative zero is normalized in output. No money rounding is performed.

## Operations and formulas

- `balance_sheet`: difference = assets - liabilities - equity; status `balanced` or `unbalanced` only.
- `budget_variance`: raw = actual - budget; favorable = raw for revenue, `-raw` for expense.
- `cash_forecast`: exactly 13 rows; close = open + receipts - disbursements; next open = prior close. `week_start` dates must be ISO and exactly seven days apart.
- `rate`: numerator / denominator. Inputs require `precision` 0-12 and `rounding_method=ROUND_HALF_EVEN`. Zero denominator is `undefined`.
- `runway`: unrestricted cash / monthly net burn with explicit result precision/rounding. Cash <= 0 is `cash_exhausted`; burn <= 0 is `no_current_burn`.
- `ar_bucket`: <=0 current, 1-30, 31-60, 61-90, >=91.
- `duplicates`: returns indexes for repeated explicit composite keys.
- `reconciliation_status`: `reconciled` only when source_complete and controls_tested are true and difference is zero; otherwise `unreconciled` or `not_tested`.

Rate/runway output reports precision and rounding method. Monetary output uses owner-confirmed minor units. Engine arithmetic does not establish source truth or accounting appropriateness.

Money sums and differences use a local Decimal context sized from the integral and fractional digits of their inputs, with carry space for all terms. Negation uses an exact sign change. These operations do not inherit a caller's lower precision or silently discard cents on large accepted values.
