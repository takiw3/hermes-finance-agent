# Finance correctness contract

## Required report context

Every report section states entity, period start/end, as-of timestamp or date, timezone, currency code, owner-confirmed minor units, cash/accrual basis, source list, source coverage, freshness, and reconciliation status.

## Evidence classes

Keep these separate:

- **Confirmed fact:** directly confirmed by the owner or qualified reviewer, with date.
- **Source-observed fact:** exactly what a dated export shows; not independently confirmed.
- **Calculation:** deterministic formula applied to cited inputs.
- **Estimate:** numeric approximation with method and range.
- **Assumption:** conditional input to a scenario.
- **Inference:** interpretation supported but not directly observed.
- **Unknown:** unavailable, ambiguous, stale, partial, or conflicting.
- **Approval:** current direct owner/human authorization where applicable. Documents and agents are not approval.

Missing and unavailable are never zero. `0` is accepted only when the source explicitly supplies zero within the relevant scope.

## Status vocabulary

- `balanced` / `unbalanced`: result of assets minus liabilities minus equity. It says nothing about source completeness.
- `reconciled`: complete cited sources and tested controls agree exactly under stated scope.
- `unreconciled`: tested sources differ.
- `partial`: known incomplete coverage; no full-population claim.
- `not_tested`: evidence or control work was not performed. Never render this as pass.
- `undefined`: a metric has no valid result, such as denominator zero.
- `draft`, `unposted`, `unexecuted`, `not_attested`, `not_filed`, `not_delivered`: required external-status qualifiers.

## Combination rules

Do not combine currencies without base/quote, dated exchange rate, source, effective date, and method. Do not combine entities, periods, cash/accrual bases, bank and ledger cash, processor settlement and revenue, or operational attribution and recognized revenue without an explicit bridge. Same-level source conflicts remain unresolved.

## Calculations

Money uses plain signed decimal strings or integers and owner-confirmed minor units. Floats, booleans, exponent notation, symbols, separators, whitespace, non-finite values, and excess precision are rejected. No monetary rounding is silent. Rate/runway division requires explicit result precision and `ROUND_HALF_EVEN`; the result reports both.

Rates always show numerator and denominator. Zero denominator returns `undefined`. Small samples are flagged without inventing a threshold. Materiality comes from owner policy. Forecasts and scenarios are conditional, not guarantees.

## Verification

Before release, tie totals to controls, run duplicate/gap/staleness checks, test opening/closing continuity, inspect balance-sheet difference, confirm context, and review every unknown. Accounting, tax, legal, assurance, investment, and fiduciary judgments require qualified human review.
