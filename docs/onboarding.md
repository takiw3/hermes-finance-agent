# Onboarding

## Objective

Establish one business tenant, explicit reporting conventions, local source ownership, and decision requirements before analysis. Onboarding creates no connection, credential, schedule, or recurring job.

## Required interview

Capture, in order:

1. Business/entity name and legal/reporting scope. If multiple businesses are involved, stop and require separate profiles or explicitly separated local workspaces.
2. IANA timezone and the reporting as-of convention. Offset-aware timestamps are required for deterministic requests.
3. Reporting currency code and owner-confirmed minor units. A three-letter format is not proof of ISO 4217 membership.
4. Cash or accrual accounting basis. `mixed` is invalid.
5. Fiscal year-end, fiscal periods, weekly start day, and close calendar.
6. Owner-approved materiality policy. Do not invent a dollar or percentage threshold.
7. Management-report cadence and named decision owners.
8. Source owners and local export locations for bank/processor, locked ledger/TB, AR/AP, contracts/pricing, and budget/forecast.
9. Qualified accounting, tax, legal, assurance, and investment contacts where relevant.
10. Retention and deletion policy for local working artifacts.

## Source registry

For each source record `source_id`, hierarchy level, owner, source type, local path, entity, period, extract as-of, timezone, currency, basis, row count, coverage, freshness, checksum when available, and limitations. Never collect login credentials or direct account access.

If an input is unavailable, record `unknown` or `unavailable` plus the consequence. Do not write zero. If two final ledgers conflict, register both and mark the conflict unresolved.

## Completion criteria

Onboarding is complete only when one tenant is confirmed, core reporting context is explicit, source owners are known, and privacy rules are accepted. It may be partially complete if blocked outputs are listed. A profile with no owner data remains `not configured`; that is not an error and is not permission to search for data.

## First safe task

Start with a source-registry and snapshot exercise using synthetic or redacted exports. Run data-quality validation before management reporting. Do not begin with a request to pay, post, file, close, reconcile, send, change, or schedule anything. Those requests are always refused and routed to an authorized human.
