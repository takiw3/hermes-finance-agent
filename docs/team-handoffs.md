# Team handoffs

## Ownership

Jarvis coordinates priorities and decisions. Marketing owns market messaging and claims. Sales owns pipeline and CRM source truth. Customer Support owns service operations. Developer owns product and engineering systems. Ads owns paid-media source truth. Finance owns financial analysis, reporting, and planning. Finance does not own revenue-attribution source truth or operational execution.

## Required fields

Every handoff includes:

- `handoff_id`, `from=Finance`, named recipient, entity, period, as-of, and timezone.
- The business request and decision needed.
- Redacted aggregates labeled as confirmed facts, source observations, calculations, estimates, assumptions, or inferences.
- Currency, owner-confirmed minor units, basis, source coverage, freshness, and reconciliation status.
- Unknowns, limitations, responsible human owner, due date, and local artifact path.
- `contains_raw_financial_data=false`, `is_approval=false`, and delivery status.

Draft is not delivered. Only exact evidence from the target system can support `delivered_with_evidence`; otherwise state `drafted` or `delivery_not_tested`.

## Redaction

Exclude raw transactions, customer/vendor/employee identity, account and routing details, tax identifiers, payroll, card data, credentials, and hidden source attachments. Use synthetic/redacted IDs where row-level references are necessary. Never put raw finance data in Kanban.

## Examples

- Finance to Sales: ask why reconciled collections differ from CRM closed-won totals. Provide aggregate amounts and period; Sales investigates pipeline source truth.
- Finance to Marketing: provide an owner-reviewed contribution-margin scenario. Marketing owns any public claim and cannot treat the scenario as a guarantee.
- Finance to Developer: report a redacted export-control mismatch and expected/observed counts. Developer owns system diagnosis; Finance does not change production.
- Finance to Ads: request source-method clarification for paid-media attribution. Do not substitute attribution for recognized revenue or collected cash.
- Finance to Jarvis: present a decision brief with options and cash implications. The brief is not approval.

## Verification

Check recipient ownership, minimum necessary data, labels, source dates, decision, owner, due date, and delivery evidence. If any sensitive row is present, do not create the handoff.
