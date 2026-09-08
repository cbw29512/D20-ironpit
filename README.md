# The Iron Pit

**Pick D&D cards. Run a rules-driven fight. Step through every event, watch it play, or simulate the matchup X times.**

Iron Pit is a rules-first browser combat simulator. The current certified public ruleset is D&D 2024 / SRD 5.2.1. Production fights run entirely in the browser; Python remains the reference/certification oracle used by generators, audits, manifests, and CI.

## Authoritative rules

Read `docs/IRON_PIT_RULES_CONTRACT.md` for the product/combat contract.

Key principles:

- source monster/pregen cards are immutable;
- every fight gets fresh temporary combat state and fully resets afterward;
- unsupported outcome-changing mechanics fail closed;
- implement universal mechanics once instead of class/monster-specific resolver hacks;
- exact source timing/order and specific-beats-general control resolution;
- Python/browser parity is required before a capability is considered supported;
- the battle log is an audit trail, not decoration.

## Production battlefield

- Six hero slots and six monster slots.
- Only certified runnable cards can enter automated combat.
- Duplicate monsters remain separate combatants with independent HP/state.
- No public starting-distance control or kiting loop.
- Card state shows current HP, conditions, concentration, buffs/debuffs, death/down states, and other supported combat state.

## Execution modes

All modes use the same canonical combat resolution path:

- **FIGHT / Watch** — play the fight automatically.
- **STEP FIGHT** — pause after each resolved event.
- **WATCH REST** — continue the same already-resolved Step session; no reroll/restart.
- **REPLAY** — reproduce a seeded fight exactly.
- **TURBO X** — run the matchup repeatedly without animation/rendering overhead and report win/loss/draw statistics.

Turbo stores lightweight fight summaries/seeds. Selecting a fight regenerates the exact seeded combat for Step/Watch/log review. Engine-rule errors are excluded from win-rate denominators and remain reproducible by seed.

## Rules audit

Resolved events can expose expandable rules evidence, including where applicable:

- original and accepted dice;
- Advantage/Disadvantage sources;
- rerolls/replacements;
- modifiers and totals;
- AC/DC checks;
- typed damage components;
- defenses/absorption/Temporary HP/HP transitions;
- conditions, concentration, resources, and state changes.

Audit annotation is post-resolution/evidence-only and cannot change combat mechanics.

## Content and certification

- The canonical 2024 SRD catalog contains exactly **330 monsters** with source metadata.
- The canonical hero architecture contains **12 persistent heroes × levels 1–20 = 240 possible hero snapshots**.
- Only explicitly certified monster templates and hero levels are runnable.
- Current ready/blocked counts are generated from repository state. Do not copy remembered counts into code or documentation.

Report current certification with:

```bash
python scripts/report_certification_progress.py
```

Generated authority lives in:

- `data/hero_certification_manifest.json`
- `data/monster_certification_manifest.json`

## Universal content pipeline

### Monsters

`SRD source -> source/parser audit -> detected mechanics -> universal capabilities -> runtime -> Python behavior -> browser parity -> generated artifact -> public readiness -> exact-head CI`

After adding a universal capability, re-audit all 330 monsters and promote every newly unblocked creature rather than special-casing one monster.

### Pregens

One persistent canonical hero exists per core class. A certified level derives from the previous certified level plus that level's audited combat delta. See `docs/CANONICAL_COMBAT_BUILD_POLICY.md`.

## Production architecture

- **GitHub:** source of truth and CI.
- **GitHub Pages / Netlify:** static deployment targets.
- **Browser engine:** production combat execution.
- **Python engine:** rules-reference/certification oracle; not required by the deployed site.
- **No production HTTP API/backend dependency.**

Netlify is reserved for deliberate production-hosting checkpoints; routine work should be proven through generators, local/static tests, and GitHub CI.

## Run locally

### Browser

```bash
python -m http.server 8080 --directory frontend
```

Open `http://localhost:8080`.

### Python certification/tests

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
pytest -q
```

## Certification gate

A tranche is not complete because code exists. Exact-head CI must prove, as applicable:

- source-size/architecture guards;
- capability/source audits;
- generated-static parity;
- certification-manifest parity;
- full Python suite;
- JavaScript syntax and permanent browser regressions;
- Step/Watch/Replay/Turbo invariants;
- audit non-interference;
- production browser-only/backend-free wiring;
- static deployment packaging and Netlify production-only guard.

## Current priority

Finish the universal engine capabilities in `IRON_PIT_RULES_CONTRACT.md`, then use those capabilities to unlock the remaining monster catalog and canonical pregen levels in large source-audited batches. Do not increase card counts by weakening rules fidelity.
