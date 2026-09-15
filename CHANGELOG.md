# Changelog

## Unreleased

- Preserve generic Agentic Workforce README wording and the financial-advice disclaimer without failing CI's branding check.
- Replace the history-presence check with a real reachable-history secret-pattern and sensitive-file scan; fetch full history in CI and reject incomplete scans.
- Preserve exact monetary addition/subtraction across accepted input sizes, independent of the caller's Decimal precision, with regression tests for lost cents and false balance results.

## 1.0.0 - 2026-09-11

- Initial Finance profile distribution.
- Added finance correctness and safety contracts, 29 actionable skills, schemas, templates, references, synthetic examples, offline evals, and strict Decimal calculation tooling.
- Added validation, unit, behavior, security, installation, and update tests.
