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

Re-anchored generated head before this checkpoint: `2de92340ac0e471d18e4c2cffb33107c0757d915`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **151**
- Blocked: **179**
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

## Current CI blocker

Generated head `2de92340ac0e471d18e4c2cffb33107c0757d915` is a `github-actions[bot]` generated-content commit. GitHub Actions CI run #7779 on that exact head concluded `action_required` before certification jobs executed.

Affected scope: the complete exact-head certification gate, not an individual monster, pregen, or combat rule.

Classification: **technical CI/authorship gate**, not a rules/product decision.

Fastest safe resolution: this human-authored ledger-only checkpoint changes no runtime behavior or generated certification data and retriggers exact-head CI against the already-earned 151-monster / 24-pregen state.

## Next priority

Do not add mechanic scope until exact-head CI executes on this checkpoint. If CI fails, fix the first real Iron Pit failure before adding scope. Once exact-head CI is green, regenerate/read blocker yields and implement the highest-leverage remaining universal primitive, with Python/browser parity and permanent CI coverage, then regenerate all canonical certification artifacts.