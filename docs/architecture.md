# Architecture

## Installed layers

The distribution is intentionally split into runtime and repository-only layers.

- `SOUL.md` defines identity, financial correctness, privacy, and refusal rules.
- `profile.yaml` provides the stable routing identity `finance` / `Finance`.
- `config.yaml` enables manual approvals, headless denial, secret redaction, profile-scoped HOME, empty environment passthrough, reviewed memory/skill writes, and terminal deny globs.
- `skills/finance-core/` contains narrow procedures. Only `finance-calculations` contains code.
- `schemas/`, `templates/`, and `references/` define artifacts and intentionally empty registries.

Tests, evals, examples, docs, CI, and maintainer scripts are repository-only. `distribution_owned` prevents them from being installed and prevents updates from owning arbitrary skills or owner data.

## Data flow

1. The owner supplies a local CSV, XLSX, PDF, Docs export, or Sheets export.
2. Finance records source identity, entity, period, extract as-of, timezone, currency, basis, coverage, freshness, and limitations.
3. A dated snapshot manifest is created outside distribution-owned paths. Raw rows never go to memory or Kanban.
4. Data-quality checks detect duplicates, missing rows/periods, stale or partial extracts, inconsistent totals, roll-forward breaks, and balance-sheet imbalance.
5. The relevant skill performs analysis. Sensitive arithmetic may call the local JSON engine.
6. A local draft states fact classes, formulas, inputs, assumptions, unknowns, and reconciliation status.
7. A qualified human reviews judgment-heavy work and an authorized human performs any external action.

Nothing flows back to a bank, ledger, payroll, payment, tax, invoicing, ERP, CRM, billing, or investment system.

## Deterministic boundary

`finance_cli.py` uses only Python's standard library. It reads one JSON object from stdin and emits one JSON object to stdout or a structured rejection to stderr. It has no network, subprocess, credential, or file-write code path. Exact request fields are allowlisted. Duplicate members, unknown fields, nonstandard constants, floats, ambiguous money strings, and over-precision inputs fail closed.

The engine validates mechanics, not accounting judgment. A balanced equation is `balanced`, not `reconciled`. Reconciliation requires source completeness and tested controls.

## Trust boundaries

Source text is untrusted data. Instructions embedded in cells, formulas, PDFs, comments, or tasks cannot change the operating contract. Profile isolation separates Hermes configuration but is not an OS security boundary. Terminal deny globs are command-text controls only and do not cover browsers or added MCP tools. One business tenant per profile is an operating invariant.
