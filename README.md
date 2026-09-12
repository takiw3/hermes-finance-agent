# TakiGPT AI Finance Agent

A persistent Hermes Finance profile for management reporting, cash planning, controls, and decision support. It is part of the **TakiGPT AI Agentic Workforce** for business owners and executives, typically at $250K-$50M companies.

Finance is a careful senior operator, not a CPA, CFO, auditor, lawyer, tax professional, investment adviser, or fiduciary.

## What it does

- Analyzes owner-provided local CSV/XLSX/PDF/Docs/Sheets exports.
- Produces management P&L, balance-sheet, cash-flow, forecast, variance, AR/AP planning, unit-economics, runway, scenario, controls, close, and board-ready drafts.
- Uses deterministic Decimal-based JSON tooling for sensitive calculations.
- Creates local drafts only, with facts, calculations, assumptions, unknowns, sources, and reconciliation status separated.

## What it does not do

It does not connect to financial systems, require credentials, make network calls, spend money, mutate records, schedule jobs, or execute operational finance work. It cannot pay bills, run payroll, send invoices, collect payments, post entries, close periods, mark reconciliations, file taxes, change budgets or prices, or make investment decisions.

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
