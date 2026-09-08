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

Re-anchored generated head before this checkpoint: `21d43fe655e3b129bad12840c1c41fd61334eb6c`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **152**
- Blocked: **178**
- Merrow is newly machine-earned after the universal simple attack parser was corrected to preserve dual-mode source grammar such as `reach 5 ft. or range 20/60 ft.`.
- The parser now retains both melee and ranged Harpoon forms plus the existing universal forced-pull rider; no Merrow-specific combat resolver branch was added.
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

Exact-head CI #7815 failed in Python certification because Merrow's printed Harpoon was absent from the generated runtime. The generic attack parser stopped its range clause at the period in `reach 5 ft. or range 20/60 ft.`, producing only Bite and Claw and triggering `source-attack-count-mismatch` plus `forced-movement-source-mismatch`.

Affected content: **Merrow directly**; the parser defect could affect any future canonical attack using the same dual-mode reach/range grammar.

Classification: **technical parser blocker**, autonomously fixable. No Chris rules/product decision was required.

Resolution: the universal parser now consumes the complete range clause through `. Hit:` rather than assuming no internal period. Permanent Python and browser tests pin both Harpoon modes, exact range/reach values, and the 15-foot `toward_source` forced movement. Generated artifacts promoted Merrow through the normal audits to **152/330**.

## Next priority

Verify exact-head CI on this human-authored checkpoint. If CI fails, fix its first real failure before adding scope. Once exact-head CI is green, regenerate/read blocker yields and implement the highest-leverage remaining universal primitive with Python/browser parity and permanent CI coverage, then regenerate all canonical certification artifacts.