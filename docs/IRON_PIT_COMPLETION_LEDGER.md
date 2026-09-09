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

Re-anchored generated head before this checkpoint: `a3f1b003b504447d5ee98a667f326575bc9b0027`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **152**
- Blocked: **178**
- Fire Giant now has a runtime template after the generic simple-hit grammar learned the chained implicit-target form `and has Disadvantage ...`; this compiles its printed Hammer Throw through existing universal forced-push and timed next-attack-disadvantage primitives.
- Browser serialization now preserves the universal `forcedMovement` control field and `consumeOnAttackMade` modifier field instead of dropping those immutable attack attributes at the Python/browser boundary.
- Fire Giant is **not yet counted as certified** here because the authoritative generated manifest remains 152/330 until its complete source/build/browser audit chain is green.
- No readiness flags were manually advanced.
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

## Latest blockers and resolutions

### 1. Browser serializer tail regression — fixed

While adding universal forced-movement parity, the serializer tail was accidentally replaced, removing the existing `defense_row` export. Exact-head CI failed first at static package preparation with an import error.

- Affected scope: entire static-generation/certification gate.
- Classification: **technical**, autonomously fixable.
- Resolution: restored the original serializer tail and retained only the generic parity additions for `forcedMovement` and `consumeOnAttackMade`.
- Chris decision required: **no**.

### 2. Generated artifact parity — generated state produced

The repaired source then reached static generation and correctly failed durable artifact parity because canonical generated files had changed. The feature-branch generation workflow produced head `a3f1b003b504447d5ee98a667f326575bc9b0027` rather than hand-editing those artifacts.

- Affected scope: exact-head certification gate.
- Classification: **technical generated-state synchronization**, autonomously handled.
- Current authoritative counts on that generated head remain **152/330 monsters** and **24/240 pregens**.
- The bot-authored generated head received GitHub `action_required` before normal CI jobs could execute.
- Fastest safe resolution: this human-authored no-runtime checkpoint retriggers exact-head CI against the generated state. If Fire Giant still fails certification, fix its first exact source-audit mismatch rather than promoting it manually.

## Next priority

Verify exact-head CI on this human-authored checkpoint. If CI fails, fix its first real failure before adding scope. If green and Fire Giant becomes machine-earned, re-anchor the resulting generated manifest. Only after exact-head green should the next implementation increment be selected from the current blocker-yield inventory by highest universal leverage.