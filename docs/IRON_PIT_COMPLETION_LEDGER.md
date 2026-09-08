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

Re-anchored head before this checkpoint: `c61865b75b0c5dd29a39f6721bd6bfc2f9d0c983`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **117**
- Blocked: **213**

### Canonical pregen progression

- Canonical classes: **12**
- Level snapshots audited: **240** (12 classes × levels 1–20)
- Level-1 engine-ready classes in the current progression audit: **8 / 12**
- Current Level-1 blockers: `bardic-inspiration`, `martial-arts`, `hunters-mark`, `innate-sorcery`

### Capability matrix

Current CI coverage report at the immediately preceding source commit reported:

- total capabilities: **59**
- supported: **40**
- partial: **10**
- unsupported: **8**
- arena-out-of-scope: **1**
- blocked declarations: **0**

### CI diagnosis

The latest source CI failure was not a combat resolver regression. The first real failure was a stale generated `data/roster_combat_mechanics_v1.json` artifact. The promotion workflow regenerated that checklist together with the canonical progression audit at commit `c61865b75b0c5dd29a39f6721bd6bfc2f9d0c983`.

The generated promotion commit was created by `github-actions[bot]`, so it did not recursively trigger the normal push CI. This checkpoint commit intentionally re-triggers exact-head CI on top of the regenerated artifacts.

## Locked implementation rules

1. One universal combat engine; no class-name or monster-name resolver branches when a generic capability can model the rule.
2. Monster and pregen cards are immutable source data. Fight state is temporary and discarded after combat.
3. 2024 / SRD 5.2.1 is the current certified ruleset. Unsupported outcome-changing mechanics fail closed.
4. Python is the certification oracle; browser production behavior requires parity and permanent regressions.
5. Step, Watch, Replay, and Turbo consume the same canonical resolver/event path.
6. Exact timing, resource use, conditions, buffs/debuffs, reactions, damage defenses, lethal overrides, summons/forms, and boss mechanics remain auditable.
7. Certification is earned from source/runtime/build/fingerprint/resource evidence; never by flipping readiness flags.

## Next priority

After exact-head CI is green, prefer the smallest reusable primitive that unlocks multiple blocked snapshots or monsters. For Level 1 pregens, investigate the four remaining blockers as generic mechanics/data before writing any class-specific code.
