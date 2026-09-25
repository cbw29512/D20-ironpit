# 2014 Life Cleric current-main re-anchor audit

Anchor: `b59fb857425593b20b96233bd1b6d47e0eb177e7` (main after 2014 Devotion Paladin 20).

## Objective

Re-anchor Seraphine Dawnshield as one persistent 2014 Life Cleric progression from level 1 through 20 without recreating the character at each level and without importing stale engine state.

## Verified current-main baseline

- 2014 certified hero snapshots: 100/240.
- Complete 2014 classes currently registered: Fighter, Barbarian, Rogue, Monk, Paladin.
- 2014 Life Cleric is not registered in `certified_hero_progressions.py`.
- Existing PR #366 / `feat/2014-life-cleric-level20-reanchor` is stale and conflicts with current main; it must not be merged wholesale.
- Current main already contains later universal work from the Paladin tranche. Reconciliation must preserve that work.

## Semantic inventory before code

The stale Cleric tranche identifies these combat semantics. Each must be reconciled against current main before porting:

1. **Turn Undead / Destroy Undead** — reuse universal saving throws and the documented 2014 Iron Pit Trembling arena mapping; source data owns DC/range/resource/source name.
2. **Preserve Life** — reusable pooled healing with a 50%-max-HP cap and Undead/Construct exclusions; no Cleric-name resolver.
3. **Blessed Healer / Disciple of Life / Supreme Healing** — reusable healing modifiers/riders; source owns numeric parameters.
4. **Divine Strike** — reusable once-per-turn weapon-hit damage rider.
5. **Divine Intervention** — reusable resource/chance/action/healing composition; level 20 removes the percentile gate rather than creating a second resolver.
6. **Dwarven Resilience** — defender-owned poison save Advantage through generic effect tags/buff matching, never attacker-side Dwarf dispatch.
7. **Death Ward** — reusable timed zero-HP replacement / nondamage instant-death prevention.
8. **Spiritual Weapon / persistent spell attacks** — reusable persistent spell-attack lifecycle, not spell-name dispatch.
9. **Spirit Guardians / persistent hazards and area effects** — reusable area/timing/damage primitives.
10. **Mass healing** — reusable group/area healing selection and allocation.

## Re-anchor rule

Do not copy the stale branch wholesale. For every changed universal file in #366:

1. compare stale branch behavior to current main;
2. keep current-main behavior when the primitive already exists;
3. port only the missing semantic remainder;
4. add/retain Python reference tests;
5. add/retain browser parity tests;
6. register Seraphine levels only after the complete progression passes fail-closed audits;
7. regenerate artifacts through repository generators only.

## Next implementation tranche

Start with the smallest missing reusable primitive required by Cleric level 1-2 after checking current main. Then build Seraphine from level 1 and advance the same progression one level at a time through 20. Batch safe level deltas before running the full certification gate.
