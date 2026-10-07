# Pregen Implementation Guide

Read `SOUL.md`, this file, and the exact class/subclass source for the edition.

## Order

1. Build/reconcile **2014 first**.
2. Decompose each feature by behavior, never by feature name.
3. Search monster and pregen implementations for equivalent primitives.
4. Reuse all compatible universal mechanics.
5. Bind source parameters only.
6. Build 2024 from the same primitives.
7. Add only genuine 2024 semantic differences.

A changed action cost, DC, dice, range, duration, resource count, or timing is normally data,
not a reason for a second engine.

## Example — Lay on Hands

Behavior:
`resource-backed healing and/or condition removal with printed targeting and action cost`.

Reuse:
- resource primitive
- healing action
- condition-removal action
- standard range/target rules

If 2014 and 2024 use different action costs, bind that per edition. Do not create separate healing
or condition-removal engines because both features are called Lay on Hands.

## Pregen state rule

Character/card data is immutable. HP, resources, buffs/debuffs, conditions, concentration,
temporary effects, and other fight changes live only in combat state and reset correctly.

## Done means

RAW edition source reconciled, 2014 complete first, shared mechanics reused in 2024, only true
edition differences scoped, Python/browser parity proven, snapshots/generated outputs refreshed.

Use `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md` and
`docs/CANONICAL_COMBAT_BUILD_POLICY.md` when build choices or source binding are ambiguous.
