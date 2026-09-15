# Testing

## Offline commands

```bash
python3 scripts/validate.py
python3 scripts/validate.py --history
python3 scripts/run_evals.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
bash tests/installation/test_install.sh
bash tests/update/test_update_preserves_owner_data.sh
python3 tests/update/test_version_compatibility.py
```

All executable finance logic is developed test-first. The recorded RED runs include the missing initial engine and later money/JSON/timezone/status edge cases; GREEN runs execute the real module and CLI.

## What passing means

- **Validator:** required layout, exact identity/version/ownership, config invariants, skill contracts and uniqueness, JSON schemas/templates, empty registries, eval coverage, branding, links, CI pinning, no inherited integration residue, no runtime network/shell path, and no obvious credential/binary owner data.
- **History scan (`--history`):** scans reachable commit messages and each unique committed file blob, including files later deleted. It flags credential filenames, known secret patterns, and unreviewed binary/symlink content. A shallow or unreadable history is not a pass. CI fetches full history before this check. This is pattern-based screening, not proof that all personal information is absent; semantic review is still required. Public author/brand credits and GitHub noreply commit attribution are intentional.
- **Unit tests:** Decimal parsing, owner-confirmed precision, no silent money rounding, duplicate JSON members, NaN/Infinity, output NaN refusal, oversized coefficients, negative zero, context/entity/period/basis/timezone validation, rates, runway, 13 dated weeks, variance signs, AR boundaries, balance equation, duplicates, and evidence-based reconciliation status.
- **Regression tests:** README accepts generic Agentic Workforce positioning without removing safety requirements; deleted historical secrets and credential files are detected without printing secret values; monetary addition/subtraction retain cents beyond default Decimal precision and under a lower-precision calling context.
- **Behavior/security tests:** operator skill sections, distinct procedures, schema pairing, report metadata, empty reference registries, runtime import boundary, prompt-injection/privacy text, and denial-limit disclosures.
- **Installation:** static payload checks always run. When `hermes` exists, a real local install runs with throwaway `HOME` and `HERMES_HOME`, then exact installed paths are inspected.
- **Update:** when `hermes` exists, owner sentinels and custom skill/config content are created only in a throwaway profile, update is run, and exact files are read back.

## What passing does not mean

Case-file validation proves corpus structure and coverage, not model behavior. Every model-backed case is `not_run` unless an actual model runner executes it. This distribution includes no model runner or credentials.

Live bank/accounting/payroll/payment/tax/ERP/CRM/billing tests are prohibited and `not_run`. Browser and added-MCP controls are `not_run`. Published-URL installation is network-dependent and opt-in, so default runs mark it `not_run`. A release-tag matrix is not claimed without a reviewed local Hermes source fixture. The actual `approvals.deny` matcher is not replaced with a homegrown fnmatch test; if no stable offline public matcher harness is available, it is honestly `not_run`.

## Counts

Each command prints pass/fail/not_run where applicable. A green exit with not_run items means only the named offline assertions passed. It does not upgrade skipped model, live-system, network, matcher, or version claims.
