# 2024 Fighter Level 17 — engine inventory

## Scope

This audit is intentionally performed before implementing or certifying the canonical level-17 Fighter snapshot. It records which combat-facing level-17 changes are already represented by universal Iron Pit capabilities so the progression does not add Fighter-specific runtime code unnecessarily.

## Existing authoritative repository rules

`backend/app/content/level_resources.py` already encodes the 2024 Fighter resource progression independently of any named pregen:

- `fighter_action_surge_uses(17)` returns **2**.
- `fighter_indomitable_uses(17)` returns **3**.
- `fighter_second_wind_uses(17)` remains **4**.

The same module keeps the 2014 entry points separate (`fighter_2014_*`) even where a resource progression currently delegates to an equivalent universal calculation. That separation must remain intact.

## Existing universal data/runtime path

`backend/app/content/fighter_progression.py` derives the Fighter resource rows from the level table rather than from Karnok-specific branches. `backend/app/content/pregen_combat_profiles.py` then emits `action-surge` and `indomitable` resources from those rows, and `backend/app/content/character_resource_audit.py` audits those resource counts.

Therefore the level-17 resource increases do **not** justify a new engine primitive. The next implementation should advance Karnok from the certified level-16 profile through the existing Fighter level application path and prove that the resulting snapshot exposes Action Surge 2 and Indomitable 3.

## Required certification regression for the next tranche

Before level 17 can be public-ready, focused tests should prove at minimum:

1. ruleset remains `2024`;
2. class level is 17 and prior level-16 build decisions are retained;
3. `action-surge` has 2 uses;
4. `indomitable` has 3 uses;
5. Superior Critical still uses the shared `critical_hit_minimum = 18` capability;
6. canonical profile policy, build audit, combat-stat audit, and resource audit all pass;
7. the certification registry advances only to level 17 and continues to fail closed at level 18 until that snapshot is separately audited;
8. generated browser data and durable certification artifacts are produced by the normal generators, never by manually changing READY flags.

## Engine decision

**Reuse existing universal capabilities.** No new Python or browser combat primitive is indicated by the current level-17 inventory. If implementation uncovers a mismatch between the level table, resource audit, runtime consumption, or browser parity, fix that mismatch generically and add permanent regression coverage before certification.
