# Data handling, privacy, and retention

## Data minimization

Use the least data needed for the decision. Prefer redacted aggregates, source IDs, counts, ranges, and local artifact paths. Do not collect credentials, bank account/routing details, tax identifiers, payroll records, payment-card data, employee records, customer/vendor PII, or raw transactions into memory or Kanban.

Raw owner exports belong only in an owner-controlled local working location outside distribution-owned paths. This repository ships no real business data. Issues, evals, tests, and examples use synthetic records only.

## Snapshot discipline

Every snapshot records source ID, owner, entity, period, extract as-of, timezone, currency, basis, row count, coverage, freshness, checksum when available, and limitations. A snapshot is immutable evidence of what was observed at a date. A corrected export receives a new snapshot ID; old provenance is not rewritten.

Memory can retain only approved, non-sensitive operating context. It is never live financial truth. Before using a remembered value, retrieve a current owner-provided source. Kanban handoffs contain no raw rows, account details, counterparties, credentials, or implied approval.

## Retention

The distribution does not impose a retention period. During onboarding, the owner supplies a policy for working files, drafts, and evidence. Keep nothing longer than needed. Deletion is performed by an authorized human because Finance does not change connected systems and should not silently delete owner evidence.

Updates own only the declared payload. Owner-created working data should remain outside `templates/`, `schemas/`, `references/`, and `skills/finance-core/`, because owned directories are replaced on update. Back up before updates.

## Handoffs

Redact direct identifiers. Include entity only at the minimum level needed, period, as-of, aggregate facts, methods, assumptions, unknowns, decision needed, owner, due date, and local artifact reference. Set `contains_raw_financial_data=false` and `is_approval=false`.

## Incident response

If sensitive data appears in memory, Kanban, logs, a repository, or a handoff: stop; do not reproduce it; preserve only minimal redacted evidence; notify the owner through the approved channel; remove access; rotate affected credentials through the system owner; and follow the business incident plan. Do not promise deletion from backups or connected systems without evidence.
