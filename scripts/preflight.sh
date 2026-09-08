#!/usr/bin/env bash
# Run the complete local Iron Pit certification gate before a push.
set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

trap 'echo "PREFLIGHT FAILED at line $LINENO: $BASH_COMMAND" >&2' ERR

skip_install=false
if [[ "${1:-}" == "--skip-install" ]]; then
  skip_install=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: bash preflight.sh [--skip-install]" >&2
  exit 2
fi

step() { printf '\n=== %s ===\n' "$1"; }

step "Toolchain and isolated Python environment"
command -v python3 >/dev/null
command -v node >/dev/null
python_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "$python_version" != "3.12" ]]; then
  echo "Python 3.12 is required; found $python_version." >&2
  exit 1
fi

if [[ "$skip_install" == false ]]; then
  if [[ ! -d backend/.venv ]]; then
    python3 -m venv backend/.venv
  fi
  # shellcheck disable=SC1091
  source backend/.venv/bin/activate
  python -m pip install -e 'backend[dev]' --quiet
fi

python - "$repo_root" <<'PY'
import pathlib
import sys

import app

expected = pathlib.Path(sys.argv[1], "backend", "app").resolve()
actual = pathlib.Path(app.__file__).resolve()
if expected not in actual.parents:
    raise RuntimeError(f"Imported app from {actual}, expected it under {expected}.")
print(f"Python import root: {actual}")
PY

step "Source limits and capability coverage"
python scripts/check_source_limits.py
python scripts/check_combat_engine_coverage.py
python scripts/export_roster_mechanic_checklist.py --check
python scripts/export_runtime_monster_capabilities.py --check
if grep -Eq 'app\.content\.(legacy_monster_roster|monster_|monsters_)' backend/app/content/roster.py; then
  echo "Forbidden legacy monster-roster reference found in roster.py." >&2
  exit 1
fi

step "Canonical generated content"
python scripts/export_browser_heroes.py
python scripts/verify_certification_manifests.py --write
git diff --exit-code -- data/hero_certification_manifest.json data/monster_certification_manifest.json
python scripts/report_certification_progress.py
python scripts/report_zero_engine_monsters.py
python scripts/report_capability_yield.py
python scripts/prepare_static_site.py
test -s frontend/data/srd_5_2_1_monsters.json
test -s frontend/browser-monsters-generated.js
test -s frontend/browser-spell-effects.js
grep -q '"id":"bless"' frontend/browser-spell-effects.js

generated_paths=(
  backend/app/content/data/combatant_capabilities_v1.json
  data/hero_certification_manifest.json
  data/monster_certification_manifest.json
  data/roster_combat_mechanics_v1.json
  frontend/browser-heroes.js
  frontend/figure-profiles.js
  frontend/browser-monsters-generated.js
  frontend/browser-spell-effects.js
  frontend/data/srd_5_2_1_monsters.json
)
git diff --exit-code -- "${generated_paths[@]}"
if [[ -n "$(git status --porcelain --untracked-files=all -- "${generated_paths[@]}")" ]]; then
  echo "Generated artifacts contain untracked drift." >&2
  git status --short -- "${generated_paths[@]}"
  exit 1
fi

step "Python rules-reference suite"
(cd backend && python -m pytest -q)

step "Browser syntax and regression suite"
for file in frontend/*.js; do
  node --check "$file"
done
bash scripts/run_browser_tests.sh

step "Browser-only production wiring"
api_base_marker='IRON_PIT_''API_BASE'
if grep -R -q "$api_base_marker" frontend scripts; then exit 1; fi
if grep -q '/api/' frontend/app.js frontend/browser-execution.js; then exit 1; fi
if grep -q 'createSeededDice' frontend/app.js frontend/battle-lab.js frontend/browser-execution.js; then exit 1; fi
if grep -q 'window.IRON_PIT_DICE[[:space:]]*=' frontend/app.js frontend/browser-execution.js; then exit 1; fi
if grep -Eq 'runEncounter|IRON_PIT_DICE' frontend/browser-audit.js; then exit 1; fi
test ! -e render.yaml
test ! -e frontend/config.js
test ! -e scripts/write_frontend_config.py
grep -q 'IRON_PIT_BROWSER_ENGINE' frontend/browser-execution.js
grep -q 'runEncounter' frontend/browser-execution.js
grep -q 'IRON_PIT_BROWSER_AUDIT' frontend/browser-execution.js
grep -q 'IRON_PIT_CANONICAL_MONSTERS_READY' frontend/app.js
grep -q 'IRON_PIT_BATTLE_LAB' frontend/browser-execution.js
grep -q 'crypto.getRandomValues' frontend/browser-dice.js

step "Public entrypoints and hosting guard"
required_ids=(hero-slots monster-slots quick-test rerun-button step-fight-button next-event-button watch-rest-button)
for page in index.html frontend/index.html; do
  test -s "$page"
  for id in "${required_ids[@]}"; do
    grep -q "id=\"$id\"" "$page"
  done
  if grep -q 'id="battle-seed"\|id="instant-mode"\|id="distance"' "$page"; then exit 1; fi
  grep -q 'https://www.buymeacoffee.com/divclass016' "$page"
done
grep -q '<base href="./frontend/">' index.html
grep -q 'id="fight-button"' index.html
grep -q 'id="card-picker"' frontend/index.html
grep -q 'id="combat-fx-overlay"' frontend/index.html
grep -q 'id="turbo-replay-step-button"' frontend/index.html
grep -q '>LOAD SAMPLE<' index.html
grep -q '>LOAD SAMPLE<' frontend/index.html
if grep -qi 'http-equiv="refresh"' index.html; then exit 1; fi

root_assets=(
  battle-lab.css audit-log.css battle-lab.js browser-audit.js browser-execution.js battle-actions.js
  figure-archetypes.css figure-swarms.css figure-portraits.css figure-profiles.js figure-portraits.js
  browser-monsters-generated.js browser-monsters-expansion.js browser-condition-rules.js
  browser-action-economy.js browser-reactions.js browser-reaction-movement.js browser-champion.js
  browser-tactical-shift.js browser-undead-fortitude.js browser-zero-hp.js browser-timed-conditions.js
  browser-barbarian2.js browser-barbarian3.js browser-sneak-attack.js browser-vex.js browser-graze.js
  browser-heroic-inspiration.js browser-light-weapons.js browser-light-attack.js
  browser-standard-attack-action.js browser-source-bound-effects.js browser-ongoing-spell-control.js
  browser-modifiers.js browser-concentration.js browser-spell-effects.js browser-spell-modifiers.js
  browser-healing.js browser-cleric-channel.js browser-spell-area.js browser-spell-policy.js
  browser-spell-resolution.js browser-spell-attack-policy.js browser-spell-attack.js
  browser-precombat-spells.js battlefield-picker.js battlefield-replay.js
)
for asset in "${root_assets[@]}"; do grep -q "$asset" index.html; done

frontend_assets=(
  battlefield.css battle-lab.css audit-log.css battle-lab.js browser-audit.js browser-execution.js
  battle-actions.js figure-archetypes.css figure-swarms.css figure-portraits.css figure-profiles.js
  figure-portraits.js browser-monsters-generated.js browser-monsters-expansion.js battle-log-format.js
  battlefield-picker.js battlefield-view.js battlefield-replay.js browser-condition-immunity.js
  browser-condition-rules.js browser-action-economy.js browser-reactions.js browser-reaction-movement.js
  browser-grapple.js browser-champion.js browser-tactical-shift.js browser-undead-fortitude.js
  browser-zero-hp.js browser-timed-conditions.js browser-barbarian2.js browser-barbarian3.js
  browser-sneak-attack.js browser-vex.js browser-graze.js browser-heroic-inspiration.js
  browser-light-weapons.js browser-light-attack.js browser-standard-attack-action.js
  browser-source-bound-effects.js browser-ongoing-spell-control.js browser-modifiers.js browser-saves.js
  browser-concentration.js browser-spell-effects.js browser-spell-modifiers.js browser-multiattack.js
  browser-healing.js browser-cleric-channel.js browser-spell-area.js browser-spell-policy.js
  browser-spell-resolution.js browser-spell-attack-policy.js browser-spell-attack.js
  browser-precombat-spells.js figure-visuals.js
)
for asset in "${frontend_assets[@]}"; do grep -q "$asset" frontend/index.html; done

grep -q 'auditDetails' frontend/battlefield-view.js
grep -q 'IRON_PIT_EXECUTION' frontend/app.js
grep -q 'CONTEXT.*production' netlify.toml
grep -q 'pip install -e ./backend' netlify.toml
grep -q 'prepare_static_site.py' netlify.toml

printf '\nPREFLIGHT PASSED — local certification is clean.\n'
