#!/usr/bin/env bash
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; PASS=0; FAIL=0; NOTRUN=0
ok(){ PASS=$((PASS+1)); echo "ok: $1"; }; bad(){ FAIL=$((FAIL+1)); echo "FAIL: $1"; }; nr(){ NOTRUN=$((NOTRUN+1)); echo "not_run: $1"; }
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT; export HOME="$S/home" HERMES_HOME="$S/hermes"; mkdir -p "$HOME" "$HERMES_HOME"
if ! command -v hermes >/dev/null 2>&1; then
 nr "real update preservation (Hermes unavailable)"; nr "distribution-owned refresh"; nr "owner skill preservation"; printf 'pass: 0  fail: 0  not_run: 3\n'; exit 0
fi
OUT=$(hermes profile install "$REPO" --name finance-update-test --yes 2>&1); RC=$?
[ $RC -eq 0 ] && ok "initial install" || { bad "initial install: $OUT"; printf 'pass: %s  fail: %s  not_run: %s\n' "$PASS" "$FAIL" "$NOTRUN"; exit 1; }
P="$HERMES_HOME/profiles/finance-update-test"
mkdir -p "$P/local/snapshots" "$P/memories" "$P/sessions" "$P/logs" "$P/skills/owner/custom"
printf SENTINEL > "$P/local/finance-operating-profile.json"; printf SENTINEL > "$P/local/snapshots/dated.json"
printf SENTINEL > "$P/memories/owner.md"; printf SENTINEL > "$P/sessions/owner.json"; printf SENTINEL > "$P/logs/owner.log"
printf SENTINEL > "$P/.env"; printf SENTINEL > "$P/auth.json"; printf SENTINEL > "$P/skills/owner/custom/SKILL.md"
printf '\n# owner override\n' >> "$P/config.yaml"; printf stale > "$P/templates/stale.template.json"
OUT=$(hermes profile update finance-update-test --yes 2>&1); RC=$?
[ $RC -eq 0 ] && ok "real local update" || bad "real local update: $OUT"
for f in local/finance-operating-profile.json local/snapshots/dated.json memories/owner.md sessions/owner.json logs/owner.log .env auth.json skills/owner/custom/SKILL.md; do
 [ "$(cat "$P/$f" 2>/dev/null)" = SENTINEL ] && ok "preserved $f" || bad "preserved $f"
done
python3 - "$P/config.yaml" <<'PY'
from pathlib import Path
import sys
assert '# owner override' in Path(sys.argv[1]).read_text()
PY
[ $? -eq 0 ] && ok "preserved config override" || bad "preserved config override"
[ ! -f "$P/templates/stale.template.json" ] && ok "removed stale owned template" || bad "removed stale owned template"
[ -f "$P/skills/owner/custom/SKILL.md" ] && ok "preserved owner skill namespace" || bad "preserved owner skill namespace"
printf 'pass: %s  fail: %s  not_run: %s\n' "$PASS" "$FAIL" "$NOTRUN"; [ "$FAIL" -eq 0 ]
