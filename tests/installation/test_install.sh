#!/usr/bin/env bash
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PASS=0; FAIL=0; NOTRUN=0
ok(){ PASS=$((PASS+1)); printf 'ok: %s\n' "$1"; }
bad(){ FAIL=$((FAIL+1)); printf 'FAIL: %s\n' "$1"; }
nr(){ NOTRUN=$((NOTRUN+1)); printf 'not_run: %s\n' "$1"; }
check(){ if "$@"; then ok "$*"; else bad "$*"; fi; }
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
export HOME="$S/home" HERMES_HOME="$S/hermes"; mkdir -p "$HOME" "$HERMES_HOME"
check test -f "$REPO/distribution.yaml"
check test -f "$REPO/SOUL.md"
check test -f "$REPO/config.yaml"
check test -f "$REPO/profile.yaml"
N=$(python3 - "$REPO" <<'PY'
from pathlib import Path
import sys
print(len(list((Path(sys.argv[1])/"skills/finance-core").glob("*/SKILL.md"))))
PY
)
[ "$N" = 29 ] && ok "29 finance skills present" || bad "29 finance skills present; found $N"
N=$(python3 - "$REPO" <<'PY'
from pathlib import Path
import sys
print(len(list((Path(sys.argv[1])/"schemas").glob("*.schema.json"))))
PY
)
[ "$N" = 11 ] && ok "11 schemas present" || bad "11 schemas present; found $N"
python3 - "$REPO" <<'PY'
from pathlib import Path
r=Path(__import__('sys').argv[1]); b=(r/'distribution.yaml').read_text()
owned=['distribution.yaml','profile.yaml','SOUL.md','config.yaml','templates','schemas','references','skills/finance-core']
assert all(f'  - {x}\n' in b for x in owned)
assert 'skills\n' not in b and 'env_requires:' not in b
for x in ['vendor','THIRD_PARTY_NOTICES.md','skills/integrations','cron']:
 assert not (r/x).exists(),x
PY
[ $? -eq 0 ] && ok "manifest ownership and exclusions" || bad "manifest ownership and exclusions"
if command -v hermes >/dev/null 2>&1; then
  OUT=$(hermes profile install "$REPO" --name finance-install-test --yes 2>&1); RC=$?
  [ $RC -eq 0 ] && ok "real local Hermes install" || bad "real local Hermes install: $OUT"
  P="$HERMES_HOME/profiles/finance-install-test"
  if [ -d "$P" ]; then
    python3 - "$P" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); owned={'distribution.yaml','profile.yaml','SOUL.md','config.yaml','templates','schemas','references','skills'}
runtime={'cron','sessions','home','memories','logs','plans','workspace','skins','.profile_meta.yaml'}
actual={x.name for x in p.iterdir()}
assert owned <= actual, owned-actual
assert actual <= owned | runtime, actual-(owned|runtime)
assert len(list((p/'skills/finance-core').glob('*/SKILL.md')))==29
for x in ['README.md','docs','evals','examples','scripts','tests','.github','LICENSE']:
 assert not (p/x).exists(),x
PY
    [ $? -eq 0 ] && ok "installed payload is narrow" || bad "installed payload is narrow"
    python3 - "$P/cron" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
assert not p.exists() or not any(x.is_file() for x in p.rglob('*'))
PY
    [ $? -eq 0 ] && ok "install creates no scheduled job" || bad "install creates no scheduled job"
  else bad "installed profile directory exists"; fi
  nr "published URL installation (network disabled by default)"
  nr "model-backed first conversation"
else
  nr "real local Hermes install (binary unavailable)"
  nr "installed payload readback"
  nr "published URL installation"
  nr "model-backed first conversation"
fi
printf 'pass: %s  fail: %s  not_run: %s\n' "$PASS" "$FAIL" "$NOTRUN"
[ "$FAIL" -eq 0 ]
