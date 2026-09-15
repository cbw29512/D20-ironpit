# D20 Iron Pit repository instructions

## Mandatory startup gate

**Read this file before doing any Iron Pit analysis, coding, refactoring, certification, or progress reporting.** Do this on every new access/session. Do not rely on chat memory, a previous assistant summary, or an old ready-count as the operating contract.

Before changing combat code:

1. confirm the exact repository branch/commit being worked;
2. read the authority files below in order;
3. identify the active ruleset/profile (2014 or 2024) and never borrow source data from the other edition;
4. inspect the current source/runtime/tests before proposing a new mechanic;
5. use fresh generated certification/ledger output from the exact current commit for progress claims;
6. if another worker may be changing the same branch, refresh the affected files before writing so current repository truth wins.

Any durable clarification from Chris that changes combat behavior, architecture, source mapping, logging, certification, or operating process must be written into the appropriate repository authority before implementation continues.

## Authority order

Before changing combat code, read:

1. `docs/IRON_PIT_RULES_CONTRACT.md` — authoritative product/combat rules.
2. `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md` — specific battlefield/card-token/grid architecture; it supersedes older fixed-formation/deity-closing assumptions wherever they conflict.
3. `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md` — durable universal-engine and data-binding architecture.
4. `docs/IRON_PIT_AUDIT_EVENT_SCHEMA.md` — audit/event evidence contract.
5. `docs/CANONICAL_COMBAT_BUILD_POLICY.md` — canonical pregen construction.
6. current source/runtime code and permanent tests.
7. generated certification state in `data/hero_certification_manifest.json`, `data/monster_certification_manifest.json`, and any ruleset-specific generated ledger/certification artifacts used by the active branch.

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

## Universal mechanic/data/effect/source ownership rule

This separation is mandatory for every attack, aura, spell, save action, recharge action, condition rider, movement effect, resource, and future combat capability:

1. **Engine mechanic owns behavior.** The shared engine defines how an attack roll, saving throw, aura geometry, line/cone/radius, damage application, condition lifecycle, recharge check, resource spend, movement, or other primitive resolves.
2. **Creature/hero ability data owns values and configuration.** Real source data supplies the actual ability name, damage dice/type, attack/save modifiers, save ability, DC, range, reach, radius/shape/size, duration, target count, uses/day, Recharge threshold, resource cost, and configured success/failure payload. The engine must not invent or silently default an outcome-changing source value.
3. **Effects own consequences/state.** Poisoned, Frightened, damage-over-time, reaction blocking, action-economy restrictions, speed changes, buffs/debuffs, and other consequences use shared effect/condition/timed-state machinery rather than source-name handlers.
4. **Runtime source identity owns attribution/logging.** Every mechanically relevant event must retain the actual source combatant identity and actual source ability display name so logs can say what creature caused what ability/effect. Source/ability names are audit/display facts, never rule-dispatch switches.

Equivalent source abilities with different names or numbers must reuse the same mechanic when the same primitive/configuration can represent them. A new monster name is never a reason for a new resolver.

Example: an Aura primitive understands radius/emanation geometry, start-turn/enter triggers, configured saving throws, duration/lifecycle, and effect dispatch. A Dretch record supplies `Fetid Cloud`, its real radius, real duration, real use limit, real save ability/DC, and real failure effect. The Poisoned/economy restrictions are shared effects. The log attributes activation and saves to `Dretch — Fetid Cloud`. Nothing in the Aura resolver checks for `Dretch`.

If source data is missing, malformed, or imported incorrectly, fix the importer/catalog/schema or keep the combatant blocked. Never fill the gap with guessed values, fake placeholders, or monster-specific runtime code.

## Mandatory uncertainty and clarification gate

- If there is any uncertainty about RAW wording, source interpretation, timing, architecture, data mapping, user intent, or whether an existing shared mechanic already covers the behavior, stop before changing code.
- Do not guess, infer around the uncertainty, create a temporary special case, or keep coding merely to preserve momentum.
- Ask Chris one precise clarification question that isolates the unresolved decision.
- After Chris answers, write the decision into the repository before implementation continues. Rules/mechanics decisions belong in `docs/IRON_PIT_RULES_CONTRACT.md`; durable universal architecture decisions belong in `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`; battlefield/card-token/grid decisions belong in `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md`; operating/process decisions belong in `AGENTS.md`.
- If the correct authority file is itself unclear, ask before writing.
- Re-read the written decision and implement against that repository authority. Do not rely on chat memory alone for a decision that can affect future combat work.
- If a new clarification conflicts with an existing authoritative rule, stop and reconcile the conflict explicitly in the repository before changing runtime behavior.
- This gate overrides speed, convenience, and perceived momentum. Asking one targeted question is preferred to implementing the wrong abstraction.

## Arena/environment invariants

- The Iron Pit magically makes the environment survivable/hospitable for every creature. Breathing, atmosphere, aquatic biology, flight requirements, and similar survival constraints never exclude a combatant.
- Movement modes must never be used as roster eligibility filters.
- Preserve printed movement modes and printed base speeds exactly as source data; never convert Swim/Fly/Climb/Burrow speed into a generic land/base speed just to make a creature runnable.
- The battlefield is one authoritative 5-foot square grid with real combatant x/y positions.
- Voluntary movement consumes actual effective movement speed. The old free-closing/fixed-formation path is migration scaffolding only and must not remain the final combat authority.
- Creature footprint derives from immutable printed size data: Tiny/Small/Medium 1x1, Large 2x2, Huge 3x3, Gargantuan 4x4 unless a more specific supported rule changes occupied space.
- Movement, reach, range, collision, Opportunity Attacks, forced movement, auras, line of sight, and area geometry consume the same authoritative grid state.
- Arena design and AI policy prevent degenerate fleeing/kiting; do not bypass printed movement to force engagement.
- The card artwork is the moving battlefield token. Current HP, Temporary HP, conditions, buffs/debuffs, concentration, recharge/resource state, and similar live symbols are presentation overlays derived from runtime state and never rule inputs.
- Reach/range still determine legal attack geometry. Forced movement, Opportunity Attacks, speed-changing effects, Grappled/Prone interactions, and any feature that explicitly depends on movement remain real mechanics and must follow the selected ruleset.
- The arena must not create a hidden combat buff/debuff from a creature's locomotion type.

## Universal mechanic workflow

When a card exposes a missing combat mechanic:

1. classify it first: existing primitive + new configuration/trigger, or genuinely new primitive;
2. identify the smallest reusable mechanic/capability;
3. define/extend schema, immutable parameters, mutable state, timing, expiry, and reset semantics;
4. bind only real ruleset-correct source values; if the source/import is incomplete, fix that layer first;
5. implement the Python oracle;
6. implement browser-runtime parity;
7. add permanent regression/parity tests and audit evidence, including actual source combatant + ability attribution in logs;
8. regenerate native generated artifacts;
9. rerun capability/source analysis across the full active roster and canonical hero progressions;
10. allow generated certification to promote every newly unblocked card.

Specific source wording beats generic behavior. Resolve each subevent fully and update state before resolving the next.

## Monster roster momentum rule

Roster completion is the priority during monster-certification work.

- Clear a monster, regenerate/re-audit, then immediately move to the next blocker.
- Do not spend an extended tranche polishing one monster-specific edge case when the reusable mechanic cannot yet be completed cleanly.
- If one monster becomes blocked by an uncertain source interpretation, large unrelated dependency, or disproportionate implementation cost, report the exact blocker to Chris, explicitly park that monster, and continue with another blocker that can advance the roster.
- Parking a monster does not permit approximating or weakening its rules. It stays blocked until the universal capability/source issue is solved correctly.
- A shared capability should be evaluated for all monsters it can unlock, not only the monster that exposed it.
- Never inflate progress. A ready/certified count moves only when the exact current generated ledger/manifest proves promotion.

## Monsters

- Canonical 2024 SRD 5.2.1 roster: exactly 330 monsters.
- Ruleset-specific projects/branches use their own authoritative source catalog and generated ledger count. In particular, do not substitute the 2024 count or source records while certifying the 2014 roster.
- Promotion path: source -> detected mechanics -> universal capability data -> runtime -> Python/browser behavior -> generated assets -> certification -> exact-head CI.
- A monster is runnable only when every outcome-changing printed mechanic is supported or explicitly proven irrelevant under the permanent arena contract.
- Never implement a mechanic by checking a monster name when a reusable schema/capability can represent it.
- After a shared capability changes, re-audit the entire active ruleset roster; never hand-pick only the motivating monster.

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

For a ruleset-specific branch such as the 2014 roster, also run that branch's own ledger/export/source-fidelity checks. Do not treat the generic 2024 manifest commands above as proof of 2014 readiness.

## Task isolation and source hygiene

- One tranche/PR should address one coherent universal mechanic or contract change. Do not mix environment refactoring, unrelated monster traits, pregens, UI polish, and deployment work in one tranche.
- Finish or explicitly park the current tranche before opening an unrelated one.
- Do not use stale generated counts from memory. Recompute/report from the exact current commit.
- Never use a different ruleset's monster/spell/feature text as a substitute for the active ruleset. Cross-edition text may be compared for research, but only the active ruleset source can populate its runtime data.
- Do not copy outdated uploaded specs or registry dumps into the repo. If external material conflicts with current repository authority, stop and reconcile the conflict explicitly.
- Keep Netlify for deliberate production checkpoints; routine verification belongs in repository CI/local-static checks.
