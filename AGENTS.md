# D20 Iron Pit repository instructions

## Authority order

Before changing combat code, read:

1. `docs/IRON_PIT_RULES_CONTRACT.md` — authoritative product/combat rules.
2. `docs/IRON_PIT_AUDIT_EVENT_SCHEMA.md` — audit/event evidence contract.
3. `docs/CANONICAL_COMBAT_BUILD_POLICY.md` — canonical pregen construction.
4. current source/runtime code and permanent tests.
5. generated certification state in `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json`.

Repository truth beats chat summaries, historical counts, old milestone prose, uploaded registry dumps, and stale file-library references. External/user-provided files are evidence only until reconciled against the exact current commit.

## Non-negotiable engineering contract

- Act as a systems/rules architect, not a mock-up generator.
- Never claim code, validation, refactoring, certification, or a mechanic is complete unless the literal full code/diff is produced and the required verification has passed.
- State first: define or identify the shared data schema, immutable source data, mutable combat state, lifecycle/timing, and reset behavior before execution functions.
- Error first: every new Python function/state mutation/rules calculation must use explicit `try/except` with meaningful contextual logging. Browser mutations/resolvers must expose explicit failure handling and must not silently recover by changing rules.
- No shortcuts: no mock combat paths, no monster-name/class-name/hero-name special-case resolvers, no hand-authored readiness flags, no hardcoded bypasses around the universal engine.
- Unsupported outcome-changing mechanics fail closed.
- Prefer universal capabilities plus declarative data. A monster/pregen supplies parameters; the engine supplies mechanics.
- Source cards/templates are immutable. All fight mutation belongs to temporary combat state and resets after every match.
- Python is the rules-reference/certification oracle; browser JavaScript is the production fight engine. Supported behavior requires parity.
- Step, Watch, Replay, and Turbo consume the same canonical resolver/event stream. Presentation mode never changes rules.
- Audit/logging is evidence-only. It never rolls dice, chooses actions/targets, or mutates combat results.
- Production combat is browser-only/backend-free.
- Do not weaken a valid test to make CI green. Replace an obsolete assertion only when an explicit contract change supersedes it, with equally strong coverage for the new rule.
- Keep production source modules at or below the repository source-size limit. Split modules rather than growing monoliths.

## Arena/environment invariants

- The Iron Pit magically makes the environment survivable/hospitable for every creature. Breathing, atmosphere, aquatic biology, flight requirements, and similar survival constraints never exclude a combatant.
- Movement modes must never be used as roster eligibility filters.
- Preserve printed movement modes and printed base speeds exactly as source data; never convert Swim/Fly/Climb/Burrow speed into a generic land/base speed just to make a creature runnable.
- Ordinary Pit positioning/closing is abstracted by the deity/fixed-formation policy. A creature's printed movement speed does not prevent it from reaching the position required to use an otherwise legal attack.
- Reach/range still determine legal attack geometry. Forced movement, Opportunity Attacks, speed-changing effects, Grappled/Prone interactions, and any feature that explicitly depends on movement remain real mechanics and must follow the selected ruleset.
- The arena abstraction must not create a hidden combat buff/debuff from a creature's locomotion type.

## Universal mechanic workflow

When a card exposes a missing combat mechanic:

1. identify the smallest reusable mechanic/capability;
2. define/extend schema, immutable parameters, mutable state, timing, expiry, and reset semantics;
3. implement the Python oracle;
4. implement browser-runtime parity;
5. add permanent regression/parity tests and audit evidence;
6. regenerate native generated artifacts;
7. rerun capability/source analysis across the full 330-monster roster and canonical hero progressions;
8. allow generated certification to promote every newly unblocked card.

Specific source wording beats generic behavior. Resolve each subevent fully and update state before resolving the next.

## Monsters

- Canonical 2024 SRD 5.2.1 roster: exactly 330 monsters.
- Promotion path: source -> detected mechanics -> universal capability data -> runtime -> Python/browser behavior -> generated assets -> certification -> exact-head CI.
- A monster is runnable only when every outcome-changing printed mechanic is supported or explicitly proven irrelevant under the permanent arena contract.
- Never implement a mechanic by checking a monster name when a reusable schema/capability can represent it.
- After a shared capability changes, re-audit all 330; never hand-pick only the motivating monster.

## Generated artifacts: never hand-edit

Generated files are outputs, not authoring surfaces. Change authoritative schema/data/runtime first, then run the repository exporter.

Runtime monster capability registry:

```bash
python scripts/export_runtime_monster_capabilities.py
python scripts/export_runtime_monster_capabilities.py --check
```

Certification manifests:

```bash
python scripts/verify_certification_manifests.py --write
git diff --exit-code -- data/hero_certification_manifest.json data/monster_certification_manifest.json
python scripts/report_certification_progress.py
```

Static/browser artifacts:

```bash
python scripts/export_browser_heroes.py
python scripts/prepare_static_site.py
git diff --exit-code -- frontend/browser-heroes.js frontend/figure-profiles.js frontend/browser-monsters-generated.js frontend/browser-spell-effects.js frontend/data/srd_5_2_1_monsters.json
```

Capability/source reports:

```bash
python scripts/check_combat_engine_coverage.py
python scripts/export_roster_mechanic_checklist.py --check
python scripts/report_zero_engine_monsters.py
python scripts/report_capability_yield.py
```

Never splice generated JSON/JS manually to satisfy parity.

## Required verification

From repository root unless a command says otherwise:

```bash
python scripts/check_source_limits.py
python scripts/check_combat_engine_coverage.py
python scripts/export_roster_mechanic_checklist.py --check
python scripts/export_runtime_monster_capabilities.py --check
python scripts/export_browser_heroes.py
python scripts/verify_certification_manifests.py --write
python scripts/prepare_static_site.py
```

Python rules reference:

```bash
cd backend
pip install -e '.[dev]'
pytest -q
cd ..
```

Browser syntax:

```bash
for file in frontend/*.js; do node --check "$file"; done
```

Run the complete permanent browser regression command list and production wiring/backend-free checks exactly as defined by `.github/workflows/ci.yml`; that workflow is the canonical complete CI command set. Final certification requires the exact intended commit to pass GitHub Actions CI.

## Task isolation and source hygiene

- One tranche/PR should address one coherent universal mechanic or contract change. Do not mix environment refactoring, unrelated monster traits, pregens, UI polish, and deployment work in one tranche.
- Finish or explicitly park the current tranche before opening an unrelated one.
- Do not use stale generated counts from memory. Recompute/report from the exact current commit.
- Do not copy outdated uploaded specs or registry dumps into the repo. If external material conflicts with current repository authority, stop and reconcile the conflict explicitly.
- Keep Netlify for deliberate production checkpoints; routine verification belongs in repository CI/local-static checks.
