# Iron Pit Completion Ledger

This ledger is a human-readable checkpoint only. The authoritative machine state remains:

- `data/monster_certification_manifest.json`
- `data/canonical_progression_engine_audit.json`
- `data/roster_combat_mechanics_v1.json`
- `data/combat_engine_coverage_v1.json`
- exact-head CI

Do not mark content complete from this file alone. Regenerate and verify the authoritative artifacts first.

## Current checkpoint

Branch: `feat/usable-roster-warlock-l1`

Re-anchored generated head before this checkpoint: `7b707c0aab93ab74adc79fe31ddca566610ead78`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **118**
- Blocked: **212**

### Canonical pregen progression

- Canonical classes: **12**
- Level snapshots audited: **240** (12 classes × levels 1–20)
- Certified pregen snapshots at this checkpoint: **24 / 240**
- Level-1 engine-ready classes in the regenerated progression audit: **9 / 12**
- Current genuine Level-1 blockers: `martial-arts`, `hunters-mark`, `innate-sorcery`
- `bardic-inspiration` is explicitly classified from canonical Bard metadata as `arena_out_of_scope` for Iron Pit's solo duel rather than being falsely treated as a missing runtime mechanic.

### Progression-audit correction

The progression audit previously calculated canonical `arena_ignored` metadata but did not use it when assigning feature status or blockers. That made arena-excluded features appear as planned engine gaps.

The exporter gives canonical arena-exclusion metadata precedence when deriving effective audit status, and treats `supported` plus `arena_out_of_scope` as non-blocking. A regression test locks this behavior. Bard Level 1 correctly advances from blocked to engine-ready without adding a Bard-specific runtime branch or claiming a mechanic that the arena never uses.

Regenerated audit summary:

- canonical classes: **12**
- level slots: **240**
- unique combat features: **226**
- Level-1 engine-ready classes: **9**
- feature statuses: `arena_out_of_scope=1`, `planned=183`, `supported=42`
- unique blocking features: **183**

### Capability matrix

The capability matrix remains the authoritative declaration layer. No readiness total in this ledger overrides its source/runtime evidence or certification manifests.

### CI diagnosis

The last human-authored implementation head `4eeb1e2ea96e537920d8f000ac2ab05cd5f48d91` reached the durable certification-manifest parity gate and failed because generated artifacts were stale. The generated-content workflow then promoted the corrected artifacts at `7b707c0aab93ab74adc79fe31ddca566610ead78`, including the monster manifest advancement from **117 / 330** to **118 / 330**. GitHub classified the PR workflow for that bot-authored promotion as `action_required` before creating certification jobs.

This checkpoint is intentionally human-authored and changes only this ledger so normal exact-head PR CI can execute against the already-generated state. No runtime behavior, capability declaration, fingerprint, resource audit, or readiness flag is changed here.

Monster readiness is now **118 / 330** because the generated authoritative manifest earned that result. Certified pregen snapshots remain **24 / 240**.

## Locked implementation rules

1. One universal combat engine; no class-name or monster-name resolver branches when a generic capability can model the rule.
2. Monster and pregen cards are immutable source data. Fight state is temporary and discarded after combat.
3. 2024 / SRD 5.2.1 is the current certified ruleset. Unsupported outcome-changing mechanics fail closed.
4. Python is the certification oracle; browser production behavior requires parity and permanent regressions.
5. Step, Watch, Replay, and Turbo consume the same canonical resolver/event path.
6. Exact timing, resource use, conditions, buffs/debuffs, reactions, damage defenses, lethal overrides, summons/forms, and boss mechanics remain auditable.
7. Certification is earned from source/runtime/build/fingerprint/resource evidence; never by flipping readiness flags.

## Next priority

Do not add mechanic scope until exact-head CI executes cleanly on the human checkpoint above. Once green, inspect the current blocker-yield report and the remaining Level-1 blockers (`martial-arts`, `hunters-mark`, `innate-sorcery`) and prefer the smallest reusable universal primitive with the highest cross-roster yield.