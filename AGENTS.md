# D20 Iron Pit repository instructions

Before changing combat code, read:

1. `docs/IRON_PIT_RULES_CONTRACT.md` — authoritative product/combat rules.
2. `docs/CANONICAL_COMBAT_BUILD_POLICY.md` — canonical pregen construction.
3. `docs/IRON_PIT_AUDIT_EVENT_SCHEMA.md` — audit/event evidence contract.
4. `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json` — generated current certification state.

The repository, generated audits/manifests, and permanent tests are authoritative for **implementation status**. Historical counts, old milestone prose, and conversational progress claims are not.

## Non-negotiable engineering rules

- Iron Pit public combat is currently D&D 2024 / SRD 5.2.1. Do not mix 2014 mechanics into the 2024 runtime.
- Every exposed combat mechanic must follow the selected ruleset plus explicit Iron Pit house rules in `IRON_PIT_RULES_CONTRACT.md`.
- Unsupported outcome-changing mechanics fail closed.
- Never approximate, silently ignore, invent, or hand-wave a combat-relevant rule merely to make a hero or monster runnable.
- Prefer universal capabilities and declarative data over hero-, class-, monster-, or level-specific resolver code.
- Source cards/templates are immutable; all mutation belongs to temporary combat state.
- Python is the rules-reference/certification oracle; the browser engine is the production fight engine. Keep their supported behavior equivalent.
- Step, Watch, Replay, and Turbo must consume the same canonical combat resolution path. Presentation mode must never alter rules.
- Audit/logging is evidence-only. It must never roll dice, select actions/targets, or mutate combat resolution.
- Preserve source auditing, generated-static parity, exact-head CI, deterministic/reproducible regression coverage, and production source-size limits.
- Do not weaken/delete a valid test merely to make CI green. Replace obsolete assertions only when an intentional architecture/rule change supersedes them, with equally strong coverage for the new contract.
- Production is browser-only/backend-free. Do not add a required HTTP API/server path to combat.

## Combat-engine workflow

When a hero/monster requires a missing mechanic:

1. identify the smallest universal capability actually missing;
2. define/extend shared schema/state/timing;
3. implement Python behavior;
4. implement browser behavior;
5. add permanent parity/regression tests, including edge cases and audit evidence;
6. rerun capability analysis across all 330 monsters and canonical hero progressions;
7. promote every newly unblocked card through generated certification rather than adding name-specific ready flags.

Specific source wording beats generic engine behavior. Resolve each event in exact legal order and update state before the next event.

## Canonical pregens

- One persistent named canonical hero per core class, levels 1–20: 240 possible level snapshots.
- A new level derives from the previous certified level plus that level's audited combat delta.
- Only explicitly certified levels are public/runnable.
- Combat-relevant class/subclass/species/feat/equipment/spell/resource rules must work or remain blockers.
- Noncombat-only choices do not require runtime mechanics.
- Do not create parallel same-class production identities or independently rebuilt level snapshots.

## Monsters

- The canonical 2024 SRD catalog contains exactly 330 monsters.
- Promotion is source-driven: source/audit -> detected mechanics -> universal capabilities -> runtime -> Python/browser behavior -> generated assets -> public readiness -> exact-head CI.
- A monster becomes runnable only when every outcome-changing printed mechanic is supported or explicitly proven irrelevant under the permanent arena contract.
- Re-audit all 330 after adding a shared capability; do not hand-pick only the monster that motivated the feature.

## Generated state

- `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json` are generated snapshots, never hand-authored claims.
- Regenerate only after authoritative source/runtime/generated state is correct.
- Report current counts from generated state, not remembered numbers.
- Do not keep redundant hand-maintained ready lists/checklists when generated authority already exists.

## Required certification before a tranche is complete

1. `python scripts/check_source_limits.py`
2. static/generator preparation and clean generated parity
3. certification-manifest verification
4. full Python test suite
5. JavaScript syntax plus permanent browser regression suite
6. capability/source audit checks
7. production backend-free/static wiring checks
8. exact intended commit certified by GitHub Actions

Netlify is reserved for deliberate production hosting checkpoints. Do not consume Netlify builds for routine iteration when GitHub CI/local-static validation can prove the change.
