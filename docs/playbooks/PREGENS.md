# Pregen Implementation Guide

Use this guide for classes, subclasses, feats, spells, items, level progression, and canonical player-character builds.

Read first: `SOUL.md`, this file, the exact edition source, and the current implementation for the class/feature being touched.

## What a pregen is

A pregen is a canonical, source-legal combat build expressed as immutable template/card data plus declarative bindings to the universal engine.

### Pregen/source owns

- class, subclass, level and ruleset;
- source-legal ability scores and build choices;
- AC, HP and derived source/build values;
- attack bonus, save DC and relevant ability;
- damage dice/type and weapon/spell parameters;
- legal feats, features, spells and items;
- range, duration, resource counts and use limits;
- exact printed names.

### Universal engine owns

The same mechanics monsters use: attacks, AC comparison, saves/checks, damage/healing, conditions, defenses, resources, timing, movement, concentration, recharge, zero-HP behavior, and other shared combat rules.

A feature called something different does not get a new mechanic if its behavior already exists.

Fight-only HP, resources, conditions, buffs/debuffs, concentration, Temporary HP, transformations and other runtime changes live in combat state and reset after the match.

## Add or reconcile a pregen

1. Start from exact edition source plus canonical build policy.
2. Reconcile **2014 first** for any shared mechanic.
3. Decompose every combat feature/spell/item:
   `trigger/timing -> action/resource -> attack/check/save -> damage/healing -> condition/state -> range/target/movement -> duration -> exits/reset`.
4. Read `docs/UNIVERSAL_MECHANIC_INVENTORY.md`, then search existing **pregen and monster** mechanics for each semantic piece. Prefer a listed supported capability ID over feature-name-specific code.
5. Reuse or compose universal primitives.
6. Bind source/build parameters only.
7. Advance in legal level order; never expose a higher level that silently omits a mandatory combat feature.
8. Reuse compatible primitives in 2024; add only genuine 2024 semantic differences.
9. Refresh generated snapshots/artifacts and prove Python/browser parity.
10. Regenerate the universal mechanic inventory and update audit/certification truth so player demand changes status automatically.

Use `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md` and `docs/CANONICAL_COMBAT_BUILD_POLICY.md` when build choices or source binding are ambiguous.

## Hard blocker rule

Never invent behavior to keep progression moving.

If a mandatory combat feature cannot be represented exactly:

- park the feature/level with the precise missing semantic or RAW question;
- do not certify dependent higher levels as complete;
- continue other independent work when possible;
- return to parked technical debt after the current pass is exhausted;
- ask Chris one precise question when interpretation or architecture is uncertain.

Never approximate, silently omit, create class/feature-name dispatch, or copy mechanics/numbers from another edition without source evidence.

## Example: Lay on Hands

Mechanical behavior, not name:

`edition-specific action cost -> spend healing pool -> restore HP and/or remove allowed condition -> enforce target/range/resource rules`

Reuse:

- action economy;
- resource;
- healing;
- condition removal;
- targeting.

The pregen/source supplies pool size, action cost, permitted effects and printed name. The engine supplies the generic behavior.

## Done means

Exact source/build; mandatory features represented; immutable template data; temporary/resetting fight state; universal reuse; edition isolation; Python/browser parity; generated snapshots/artifacts refreshed; certification truth current.
