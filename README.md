# TakiGPT AI Finance Agent

**Understand your numbers. Plan your cash. Make better-informed business decisions.**

A persistent Hermes profile named `finance` that turns owner-provided financial exports into management reports, cash scenarios, and decision briefs. Part of the **TakiGPT AI Agentic Workforce**, it works directly with you or prepares redacted handoffs for Jarvis, your chief of staff.

- **Author:** Taki Wong / TakiGPT AI Inc.
- **License:** MIT
- **Profile ID:** `finance` · **Display name:** Finance
- **Version:** 1.0.0

## Who it's for

Business owners, entrepreneurs, and executives, typically at $250K-$50M companies, who need a clearer view of cash, profitability, and financial risks without handing an AI control of their bank accounts or accounting records.

Use it to prepare for a weekly review, investigate a margin change, model a hiring decision, or organize the evidence your accountant needs.

Finance is a careful senior operator, not a CPA, CFO, auditor, lawyer, tax professional, investment adviser, or fiduciary.

## What it does

- **See where cash may get tight.** Build dated 13-week cash scenarios, review runway, and compare expected receipts with upcoming obligations.
- **Understand what drives profit.** Prepare management P&L reports, examine gross and contribution margins, and compare actual performance with your approved budget.
- **Make trade-offs explicit.** Model hiring, pricing, cost, and sales scenarios with visible assumptions, formulas, and sensitivities.
- **Prioritize financial follow-up.** Review receivables aging, draft payment-priority lists, and identify working-capital pressures without contacting customers or moving money.
- **Find gaps before relying on the numbers.** Check duplicates, missing periods, stale exports, control totals, and opening-to-closing balance differences.
- **Prepare for reviews with less rebuilding.** Create weekly finance briefs, owner/board reporting drafts, close-review checklists, and accountant or lender package indexes.

Inputs are owner-provided local CSV/XLSX/PDF/Docs/Sheets exports. Outputs are local drafts with sources, formulas, assumptions, unknowns, and reconciliation status made explicit. Missing information blocks the affected conclusion; it is never silently treated as zero.

## Example tasks

- "Build a 13-week cash forecast from these exports and my confirmed payment assumptions. Flag potential shortfalls and missing inputs."
- "Compare this month's actuals with the approved budget. Show revenue and expense variances separately and distinguish evidence from possible explanations."
- "Analyze margins by service using my approved cost classifications. Show which changes are supported by the data."
- "Model the cash and break-even impact of one additional hire. Use the compensation and start-date assumptions I provide."
- "Review this receivables export. Show aging buckets, disputed items, and collection priorities for my review. Do not contact anyone."
- "Prepare my month-end review: unresolved balance differences, missing support, and questions for my accountant. Do not post entries or close the period."
- "Run the weekly finance review and draft a one-page owner brief with decisions, risks, and next actions."

Start with onboarding so the agent knows your entity, reporting basis, currency, source coverage, and owner-approved policies. These are task examples, not promises of complete results from incomplete data.

## Skills

29 focused skills in [`skills/finance-core/`](skills/finance-core/). Each defines required inputs, a domain-specific procedure, deliverables, escalation rules, and verification checks.

| Skill | Produces |
| --- | --- |
| [Intake and routing](skills/finance-core/finance-intake-and-routing/SKILL.md) | A scoped brief, chosen workflow, missing inputs, and next safe action |
| [Finance onboarding](skills/finance-core/finance-onboarding/SKILL.md) | A business operating-profile draft with reporting conventions and source requirements |
| [Source registry and snapshot](skills/finance-core/source-registry-and-snapshot/SKILL.md) | A dated source inventory with provenance, coverage, freshness, and unresolved conflicts |
| [Data-quality validation](skills/finance-core/data-quality-validation/SKILL.md) | Duplicate, gap, continuity, and control-total checks with explicit exceptions |
| [Chart-of-accounts mapping](skills/finance-core/chart-of-accounts-mapping/SKILL.md) | Mapping proposals, unmapped accounts, and a source tie-out; no changes to the chart |
| [Management P&L](skills/finance-core/management-pl/SKILL.md) | Revenue, costs, profit, and variance reporting tied to approved mappings and source totals |
| [Balance-sheet review](skills/finance-core/balance-sheet-review/SKILL.md) | Accounting-equation checks, movement analysis, and unresolved balance differences |
| [Cash-flow analysis](skills/finance-core/cash-flow-analysis/SKILL.md) | A beginning-to-ending cash bridge with bank/ledger differences kept explicit |
| [13-week cash forecast](skills/finance-core/thirteen-week-cash-forecast/SKILL.md) | A dated weekly cash scenario with roll-forward checks and potential shortfalls |
| [Budget versus actual](skills/finance-core/budget-vs-actual/SKILL.md) | Amount and rate variances with explicit revenue/expense sign conventions |
| [AR aging and prioritization](skills/finance-core/ar-aging-and-prioritization/SKILL.md) | Receivables aging, exceptions, and owner-policy-based follow-up priorities |
| [AP payment planning](skills/finance-core/ap-payment-planning/SKILL.md) | An unexecuted payment-priority list with cash impacts, disputes, and review gates |
| [Working-capital analysis](skills/finance-core/working-capital-analysis/SKILL.md) | Working-capital bridges and collection, inventory, and payment-cycle metrics |
| [Unit economics](skills/finance-core/unit-economics/SKILL.md) | Per-unit revenue, variable costs, and contribution margins with defined inclusion rules |
| [Break-even analysis](skills/finance-core/break-even-analysis/SKILL.md) | Break-even volume/revenue scenarios, sensitivities, and infeasible-case warnings |
| [Runway analysis](skills/finance-core/runway-analysis/SKILL.md) | Cash/burn scenarios with explicit treatment of exhausted cash and no current burn |
| [Pricing and margin analysis](skills/finance-core/pricing-and-margin-analysis/SKILL.md) | Price, mix, and cost comparisons for a decision brief; no live price changes |
| [Scenario planning](skills/finance-core/scenario-planning/SKILL.md) | Base, upside, and downside comparisons with controlled assumption changes |
| [Variance and anomaly investigation](skills/finance-core/variance-and-anomaly-investigation/SKILL.md) | Quantified differences, tested hypotheses, rejected explanations, and next checks |
| [KPI dashboard](skills/finance-core/kpi-dashboard/SKILL.md) | A dated dashboard draft with metric definitions, formulas, sources, and data warnings |
| [Monthly close review](skills/finance-core/monthly-close-review/SKILL.md) | An evidence-based checklist of exceptions, owners, and blocked sign-offs |
| [Proposed journal-entry package](skills/finance-core/proposed-journal-entry-package/SKILL.md) | Unposted debit/credit proposals with support, balance checks, and qualified-review gates |
| [Accountant and tax package](skills/finance-core/accountant-tax-package/SKILL.md) | A document index, missing-support list, and professional-review questions; not tax advice |
| [Lender and investor package](skills/finance-core/lender-investor-package/SKILL.md) | A draft package index with disclosures and source references; no attestation |
| [Financial controls](skills/finance-core/financial-controls/SKILL.md) | A controls matrix and proposed remediation plan; no audit opinion |
| [Owner and board reporting](skills/finance-core/owner-board-reporting/SKILL.md) | A decision-led brief with scorecard, cash/risk watchouts, and source appendix |
| [Weekly finance review](skills/finance-core/weekly-finance-review/SKILL.md) | A manually requested finance brief with priorities, unresolved items, and human-owned actions |
| [Cross-team handoffs](skills/finance-core/cross-team-handoffs/SKILL.md) | Redacted, undelivered briefs with evidence, uncertainty, decision owners, and approvals needed |
| [Finance calculations](skills/finance-core/finance-calculations/SKILL.md) | Local deterministic JSON calculations with strict validation and explicit precision policies |

**Workflow skills are not live integrations or autonomous execution.** The calculation CLI supports a defined subset of operations; the broader skills guide analysis and draft preparation using Hermes tools. Forecasts remain scenarios, and accounting, tax, and assurance judgments require qualified human review.

## Working with Jarvis

Finance can work as a standalone profile or prepare results for Jarvis and separately installed specialists. It owns financial analysis and planning, not operational execution or another team's source of truth.

Handoffs state the decision needed, deliverables, sources, facts versus assumptions, unresolved checks, and required human review. Raw transactions, bank details, payroll records, and customer/vendor PII do not belong in memory or Kanban. Installing Finance does not install teammates or configure cross-agent routing. See [the handoff contract](docs/team-handoffs.md).

## What it does not do

The distribution ships no financial-system connectors, credentials, or scheduled jobs. Installation does not connect to financial systems. Its deterministic calculation CLI makes no network calls. The profile's operating policy prohibits paying bills, running payroll, sending invoices, collecting payments, posting entries, closing periods, marking accounts reconciled, filing taxes, changing budgets or prices, and making investment decisions.

Proposed entries remain **UNPOSTED**. Payment plans remain **UNEXECUTED**. Reports and packages remain **DRAFT**. These policy boundaries are not a guarantee that every possible tool route is technically blocked; see the [permission model](#permission-model).

## Requirements

- Hermes Agent `>=0.20.0`.
- A provider/model configured by the owner for the `finance` profile.
- Python standard library only for the deterministic engine.
- No environment variables, third-party packages, or credentials are required by this distribution.

The supported-version floor reflects path-aware `distribution_owned` behavior. Compatibility with every later Hermes release is not claimed. Run the included local tests against your installed version before production use.

## Install

Review the repository first, then run:

```bash
hermes profile install https://github.com/takiw3/hermes-finance-agent --alias
```

For trusted, reviewed automation only, `--yes` skips the interactive confirmation:

```bash
hermes profile install https://github.com/takiw3/hermes-finance-agent --alias --yes
```

Install copies only `distribution.yaml`, `profile.yaml`, `SOUL.md`, `config.yaml`, `templates/`, `schemas/`, `references/`, and `skills/finance-core/` into the profile. It does not copy repository tests/docs/examples, connect an account, configure a provider, create credentials, ingest data, start a process, add an MCP server, or schedule a job. The profile starts with no business data and is **not configured** for any tenant.

## First run

```bash
hermes -p finance model
hermes -p finance chat
```

Say: `Start finance onboarding for one business. Do not store raw transactions or PII.` Provide entity, timezone, reporting currency and owner-confirmed minor units, basis, fiscal calendar, materiality policy, reporting cadence, and local export paths. Keep one business tenant per profile.

## Update

```bash
hermes profile update finance
```

Update replaces only distribution-owned paths. Hermes normally preserves local config overrides; owner data should live outside owned paths. Back up first and run the throwaway-home update test for your installed Hermes version.

## Uninstall

```bash
hermes profile delete finance
```

Review and separately remove any owner-created local artifacts or backups. Uninstall does not revoke third-party credentials because this distribution never creates them.

## Permission model

`approvals.mode: manual`, headless approval denial, memory/skill write review, secret redaction, an empty environment passthrough, and terminal command deny globs provide defense in depth. The deny globs govern terminal command text only. They do not govern browser actions or added MCP tools, and they are not a complete OS sandbox. Profile isolation is not an OS security boundary. Do not add financial integrations without a separate security review.

## Testing status

Offline validation, unit, behavior, security, installation-payload, and update-preservation tests ship in this repository and use synthetic data. Model-backed evaluations, live financial-system tests, browser/MCP tests, published-URL installation, and versions not exercised locally are reported `not_run`, never passed. See [docs/testing.md](docs/testing.md).

## Limitations

- Source extraction quality depends on the supplied export; scanned PDFs may require OCR and human verification.
- The engine validates a three-uppercase-letter currency-code format but does not ship an ISO currency registry. The owner must confirm currency and minor units.
- No exchange rates, tax rates, benchmarks, materiality defaults, or accounting mappings ship.
- JSON Schema files document artifacts; repository validation checks structure but is not a substitute for independent accounting review.
- Forecasts are scenarios. Lender/investor packages are drafts, not attestations. Tax packages are organization aids, not advice or filings.

## Security

Use synthetic data in issues. Never commit credentials, bank details, tax IDs, payroll data, card data, PII, or raw transactions. Report vulnerabilities per [SECURITY.md](SECURITY.md).

## Agentic AI Academy

This agent is included in the ecosystem taught inside the [Agentic AI Academy](https://www.skool.com/agenticaiacademy), a practical community for building and operating AI agent workforces. Membership is currently listed at $97/month; verify current terms at the linked page.

## License

MIT. Copyright (c) 2026 TakiGPT AI Inc.
