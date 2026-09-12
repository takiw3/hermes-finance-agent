# Source hierarchy and conflict rules

## Hierarchy

1. Current bank statements and processor settlement records establish cash movement within their stated account and settlement scope.
2. Locked or final general ledger and trial balance establish accounting truth for the stated entity, period, basis, and ledger status.
3. AR/AP and other subledgers provide detail only when tied to authoritative control totals.
4. Signed contracts and approved, effective-dated price catalogs establish obligations and pricing.
5. Approved budgets and forecasts establish plan, not actuals.
6. Current official guidance or a qualified professional establishes tax/legal guidance. The shipped registry is empty.

The hierarchy is purpose-specific. A bank statement does not establish accrual revenue; a ledger does not prove bank availability; CRM data does not prove recognized or collected revenue.

## Conflict protocol

1. Freeze the competing observations with source IDs, dates, scopes, and checksums when available.
2. Confirm that entity, period, basis, currency, minor units, and extraction filters are comparable.
3. Check whether one source is lower in the purpose-specific hierarchy. It may explain detail but cannot silently replace higher-level truth.
4. For same-level conflicts, retain both values. Calculate and report the difference. Do not pick the newer or larger one by intuition.
5. Identify the human source owner and evidence needed to resolve it.
6. Mark dependent outputs `blocked`, `partial`, or `not_tested` as appropriate.
7. After a human resolves the conflict, create a new dated snapshot. Do not rewrite old provenance.

## Coverage and freshness

Coverage states included/excluded entities, accounts, periods, rows, and pagination. Freshness states extract as-of and whether it meets the decision's requirement. `current` is never inferred from a filename. An inaccessible field is unavailable, not pass.

## Examples

If two locked January trial balances differ by 100.00, the conflict is unresolved even if one file has a later filesystem timestamp. If AR detail totals 49,900.00 and the locked GL control is 50,000.00, report a -100.00 detail-to-control difference and stop full aging conclusions. Never post a plug or mark reconciled.
