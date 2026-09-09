# Iron Pit Completion Ledger

This ledger is a human-readable checkpoint only. The authoritative machine state remains:

- `data/monster_certification_manifest.json`
- `data/hero_certification_manifest.json`
- `data/canonical_progression_engine_audit.json`
- `data/roster_combat_mechanics_v1.json`
- `backend/app/content/data/combatant_capabilities_v1.json`
- exact-head CI

Do not mark content complete from this file alone. Certification is earned only through source/build/runtime/fingerprint/resource audits, generated artifacts, Python/browser parity, and exact-head CI.

## Current checkpoint

Branch: `feat/usable-roster-warlock-l1`

Re-anchored generated head before this checkpoint: `7f80342213ddd3c7186796f359bef1334ca4f8eb`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **152**
- Blocked: **178**
- Merrow remains machine-earned after the universal simple attack parser was corrected to preserve dual-mode source grammar such as `reach 5 ft. or range 20/60 ft.`.
- The parser retains both melee and ranged Harpoon forms plus the existing universal forced-pull rider; no Merrow-specific combat resolver branch was added.
- This total is machine-earned from `data/monster_certification_manifest.json`; no readiness flags were manually advanced.
- Continue from the generated blocker inventory rather than redoing already-certified monsters.

### Canonical pregen progression

- Canonical classes: **12**
- Level snapshots audited: **240** (12 classes × levels 1–20)
- Certified pregen snapshots: **24 / 240**
- The canonical progression audit remains the authority for which class-level features are supported, planned, or blocking.
- Combat-irrelevant features are omitted from runtime and must not block certification.

### Locked architecture

1. One universal combat engine; no class-name or monster-name resolver branches when a generic capability can model the rule.
2. Monster and pregen cards are immutable source data. Fight state is temporary and discarded after combat.
3. 2024 / SRD 5.2.1 is the current certified ruleset. Unsupported outcome-changing mechanics fail closed.
4. Python is the certification oracle; browser production behavior requires parity and permanent regressions.
5. Step, Watch, Replay, and Turbo consume the same canonical resolver/event path.
6. Exact timing, resource use, conditions, buffs/debuffs, reactions, damage defenses, lethal overrides, summons/forms, boss mechanics, and edge cases remain auditable.
7. Environmental/biological requirements are not blockers in the magically hospitable Iron Pit unless they directly change combat math or state.
8. Utility-only abilities, spells, and traits that cannot alter combat math/state are omitted rather than modeled.
9. Certification is earned from source/runtime/build/fingerprint/resource evidence; never by flipping readiness flags.

## Latest blocker and resolution

The certification chain exposed browser test-harness dependency drift after universal attack/save/resource helpers were extracted. The failures were test integration defects, not combat-engine behavior defects.

Affected scope: the exact-head certification gate, with stale isolated harnesses for Action IR reactions, generated Constrict compatibility, spell resolution, Champion, Fighter 9, Heroic Inspiration, Ongoing Spell Control, and Roll Revisions. No monster or pregen readiness state was promoted by these fixes.

Classification: **technical CI/test-contract blocker**, autonomously fixable. No Chris rules/product decision was required.

Resolution completed in this workstream:

- Generic Action IR parity now counts declarative supported reactions such as Parry and Redirect Attack rather than assuming only attacks/save/heal/removal actions exist.
- The Constrictor Snake compatibility fragment no longer duplicates canonical flat grapple-control fields inside a legacy nested `failureControl` object; the shared save helper reconstructs the same control semantics from canonical fields.
- Browser source-fingerprint coverage now preserves the complete 2024 Specter and Wraith trait sets, including `Incorporeal Movement` and `Sunlight Sensitivity`.
- The isolated spell-resolution harness now loads the universal resource/save dependency chain instead of relying on an undefined resource helper.
- `check_browser_harness_dependencies.py` now audits both array-based loader blocks and direct `load("...")` calls, including the resource dependency used by the universal spell resolver.
- `sync_browser_harness_dependencies.py` now synchronizes direct-load groups as well as array loader blocks. The feature-branch sync workflow used that generalized repair to normalize five additional stale harness closures automatically.
- Production combat code, RAW behavior, source definitions, and readiness flags were not changed by these harness repairs.

The synchronized bot-authored head `7f80342213ddd3c7186796f359bef1334ca4f8eb` then hit GitHub `action_required` before both exact-head workflows could execute. This checkpoint is a human-authored no-runtime re-anchor so those already-repaired sources can receive a normal exact-head certification run.

## Next priority

Verify exact-head CI on this human-authored checkpoint. If CI fails, fix its first real failure before adding scope. Once exact-head CI is green, regenerate/read blocker yields and implement the highest-leverage remaining universal primitive with Python/browser parity and permanent CI coverage, then regenerate all canonical certification artifacts.