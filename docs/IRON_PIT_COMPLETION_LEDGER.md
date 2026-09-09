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

Re-anchored generated head before this checkpoint: `c581cdeff11a7d6564f91196799c0ae0a8a513b1`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **153**
- Blocked: **177**
- Fire Giant has now earned certification through the generated source/build/runtime audit path after the generic simple-hit grammar and browser serialization preserved its Hammer Throw forced push and timed next-attack-made Disadvantage attributes.
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

## Latest blocker and resolution

### Bot-authored generated head cannot execute Actions — checkpoint fix applied

The generated-content workflow produced `c581cdeff11a7d6564f91196799c0ae0a8a513b1`, which advanced the authoritative manifest to **153/330 monsters** by earning Fire Giant. Because that commit is authored by `github-actions[bot]`, both exact-head CI and Browser Harness Dependencies concluded `action_required` before jobs executed.

- Affected scope: entire exact-head certification gate.
- Classification: **technical CI/authorship blocker**, autonomously fixable.
- Chris decision required: **no**.
- Fastest safe resolution: this human-authored no-runtime ledger checkpoint retriggers exact-head CI against the already-generated 153-monster state.

## Next priority

Verify exact-head CI on this human-authored checkpoint. If CI fails, fix its first real failure before adding scope. If green, select the next implementation increment directly from the current generated blocker-yield inventory, preferring the highest-leverage universal primitive across both monsters and canonical pregen snapshots.