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

Re-anchored generated head before this checkpoint: `96a28a5dafdc4e7988cce19458419f2447aca7be`

### Monsters

- Canonical SRD monsters: **330**
- Public-ready in the current generated manifest: **127**
- Blocked: **203**
- Latest earned tranche: **Specter** and **Wraith**. Their printed `Incorporeal Movement` trait is combat-irrelevant in the standard Iron Pit because the Pit has no walls, objects, obstacles, or terrain to traverse or end inside; printed flight and all other source combat data remain unchanged.
- This total is machine-earned from the generated certification manifest; no readiness flags were manually advanced.

### Canonical pregen progression

- Canonical classes: **12**
- Level snapshots audited: **240** (12 classes × levels 1–20)
- Certified pregen snapshots: **24 / 240**
- Level-1 engine-ready classes: **9 / 12**
- Current genuine Level-1 blockers remain `martial-arts`, `hunters-mark`, and `innate-sorcery` unless a newer generated progression audit proves otherwise.
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

Implementation head `b5a0aab79016734515d171f82cb1dcdbc9fc125c` successfully generated a 127-monster capability set, then `actions/upload-artifact@v4` uploaded the canonical hero artifact bytes but failed finalization with HTTP **403 Forbidden** from the artifact intermediary. The failure occurred before the remaining certification steps could run.

Classification: **technical/transient CI infrastructure blocker**, not a rules/product decision and not an Iron Pit combat failure.

Resolution: generated-content automation already promoted the authoritative 127-monster artifacts at `96a28a5dafdc4e7988cce19458419f2447aca7be`. This human-authored ledger-only checkpoint changes no runtime behavior or certification data and exists to retrigger exact-head CI against that generated state.

## Next priority

Do not add mechanic scope until exact-head CI executes on this checkpoint. If CI fails, fix the first real Iron Pit failure before adding scope; if the artifact intermediary alone fails again, treat it as infrastructure noise and preserve the generated evidence. Once exact-head CI is green, regenerate blocker yields and choose the highest-leverage remaining item, classifying it as data-only, combat-irrelevant, already handled by an existing universal primitive, or a genuine missing universal primitive.
