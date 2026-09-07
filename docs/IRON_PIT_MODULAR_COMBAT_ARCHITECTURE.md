# Iron Pit Modular Combat Architecture

This file is durable project architecture. It supplements `IRON_PIT_COMBAT_MATH_RULES.md` and is locked unless the user explicitly changes it.

## Core composability rule

A complete source ability is a composition of reusable combat primitives. Do not create a new engine mechanic merely because an ability has a different name, trigger, timing, target, resource, damage type, or numerical parameter.

Before adding any new primitive, search the capability registry for an existing primitive or combination that produces the same combat-math behavior.

Exact source ability names remain data for logs and audits. Mechanical behavior belongs to shared engine primitives.

## Separate effect from trigger

The mathematical effect and the event that causes it are separate modules.

Example:

- `On hit: target takes +1d6 fire damage.`
- `At the start of the target's turn: target takes 1d6 fire damage.`

Both use the same universal typed-damage primitive. They differ only in trigger/timing configuration.

Do not implement separate `on_hit_fire_damage` and `start_turn_fire_damage` engines.

## Orthogonal ability components

Represent abilities by composing independent components whenever possible:

- trigger: on hit, failed save, start of turn, end of turn, on damage, at 0 HP, reaction trigger, etc.
- timing/expiry: source turn, target turn, rounds remaining, save ends, concentration, permanent-for-current-fight, etc.
- target requirement: self, enemy, attacker, target hit, grappled by source, bloodied target, size restriction, etc.
- roll: attack, saving throw, ability check, automatic effect.
- effect: typed damage, healing, Temporary HP, modifier, Advantage/Disadvantage, condition, action denial, resource change, zero-HP resolution, etc.
- resource: finite uses, Recharge, spell slots, class resources, per-turn availability, etc.
- parameters: dice, flat values, DC, ability, damage type, condition, duration, uses, recharge range, and similar data.

A new source ability should normally be declarative data selecting and parameterizing these components.

## No duplicate mechanics

Different names or damage types do not justify separate engine systems.

Examples:

- fire, cold, lightning, necrotic, and slashing damage all use typed damage with a damage-type parameter.
- Bite, Claw, Sting, Slam, and a homebrew Shadow Fang use the same attack/damage primitives when their mathematical behavior is equivalent.
- `1/Day`, `2/Day`, Recharge 5-6, spell slots, and other limited-use abilities should reuse the generic resource system wherever their lifecycle can be expressed by resource parameters.

If an existing primitive plus different data expresses the source rule correctly, reuse it.

## Capability-registry gate

Every combat-relevant source ability must pass through the capability registry.

For each source ability, the registry should identify:

1. exact source ability name;
2. normalized mechanical fingerprint;
3. composed universal primitives;
4. parameters and triggers;
5. whether each required primitive is supported in Python and browser runtimes;
6. every monster, pregen, or homebrew ability with an equivalent fingerprint or reusable component;
7. how many currently blocked combatants would be unlocked by adding any missing primitive.

When a new missing mechanic is discovered:

1. search the registry for equivalent abilities across all blocked monsters;
2. verify that no existing primitive or composition already expresses it;
3. add the smallest genuinely new universal primitive only if necessary;
4. rescan the entire roster;
5. certify every newly complete monster as a batch;
6. keep true one-off edge cases at the back of the work queue.

## Scope rule

Only combat-math consequences that can change the current Iron Pit battle belong in the engine. Post-combat consequences, movement-only effects, flavor, exploration, and other outcome-neutral text are stripped before fingerprinting.

A mixed ability keeps only its current-battle mathematical components.

## Goal

The same engine must support official monsters, pregens/player characters, and homebrew combinations. Homebrew should normally be assembled from existing universal primitives. Engine changes should be required only for genuinely new combat mathematics or unusual edge cases, not for new names or novel combinations of mechanics the engine already understands.
