# Universal Engine Implementation Guide

Read `SOUL.md`, this file, and the current source/code that exposes the gap.

## A new primitive is the last option

Before adding one, ask whether existing mechanics can represent the behavior through:
condition, save/check/attack, damage/healing, resource/recharge, timing/timed effects,
targeting/area/movement, or composition of several existing primitives.

If yes: widen/reuse the generic path. If no: define the primitive state/schema first.

## Required map

`immutable source -> capability schema -> mutable combat state -> Python oracle ->
browser runtime -> serializer/generated data -> audit event -> permanent tests`

Never dispatch engine behavior on a class, monster, spell, hero, or printed ability name.

## Example — missing wake metadata

If source data already contains:
- `effect_id = unconscious`
- `ends_on_damage = true`
- `allowed_removal_action_ids = ["wake-sleeper"]`

but the failed-save pipeline drops `allowed_removal_action_ids`, do **not** build a Sleep subsystem.
Carry the generic field through schema, Python apply, serializer, browser apply, then reuse the
existing condition-removal resolver.

After widening a primitive, search monsters and pregens for other content that can now use it.

## Done means

Schema/state defined first; reset/lifecycle explicit; Python/browser equivalent; source-neutral;
serialization/parity covered; focused tests prove the primitive; newly unblocked content is re-audited.

Use `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md` and `docs/COMBAT_RESOLUTION_PIPELINE.md`
when a shared primitive, lifecycle, ordering, or hook actually changes.
