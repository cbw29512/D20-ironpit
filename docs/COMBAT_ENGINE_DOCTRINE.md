# Iron Pit Universal Combat Engine Doctrine

This document records the locked architecture rules for the D&D 5e 2024 / SRD 5.2.1 combat engine. It exists so monster, pregen, and future homebrew support all resolve through the same modular mechanics instead of source-specific code.

## Core rule

**The engine owns the mechanic. The source owns the label and parameters.**

A source can be an SRD monster, player character, spell, weapon, feat, class feature, or homebrew combatant.

The source supplies data such as:
- printed ability name used for logging/UI
- attack bonus or penalty
- save/check DC
- save/check ability
- damage dice and flat modifiers
- damage type
- range/reach/area
- duration
- target restrictions
- size restrictions
- recharge/limited-use values
- triggers and timing

The engine supplies the shared rule behavior.

## Locked universal mechanics

### Damage types
Every damage type is universal. Slashing is Slashing regardless of whether it comes from a pixie, giant, player, spell, weapon, or homebrew creature. The source changes only the math and other parameters.

Resistance, immunity, and vulnerability are resolved against the universal damage type, never against a monster-specific implementation.

Example:
- Pixie sword: attack data + small Slashing damage packet
- Giant sword: attack data + large Slashing damage packet
- Both use the same attack-roll and Slashing-damage systems.

### Mixed damage packets
Each damage packet is resolved independently before the resulting HP loss is combined.

Example: `1d8 Slashing + 1d6 Poison` against a target that is Vulnerable to Slashing and Immune to Poison:
- resolve the Slashing packet and apply Slashing vulnerability
- resolve the Poison packet and reduce it to 0 because of Poison immunity
- combine the resolved packets into the final HP loss

No resistance, immunity, or vulnerability on one damage type changes another damage packet unless the source explicitly says so.

### Damage defenses and condition defenses are separate
Damage resistance, damage immunity, damage vulnerability, and condition immunity are independent universal checks.

A creature being Immune to Poison damage does not automatically make it Immune to the Poisoned condition. A creature being Immune to the Poisoned condition does not automatically make it Immune to Poison damage. If a source has both, both are recorded and checked separately.

This rule applies to every damage type and every condition.

### Conditions
Every condition is universal. Prone is Prone regardless of source. Poisoned is Poisoned regardless of source.

The source may determine whether the condition is automatic or gated by an attack, saving throw, check, trigger, duration, size restriction, or other parameter. Condition immunity is checked by the universal condition system.

Example:
- `Pseudodragon — Sting` remains the printed/log name.
- Underneath it can compose universal Poison damage, Poisoned, Unconscious, saving-throw, duration, and immunity rules.
- Another creature can use different dice/DCs with the same underlying mechanics.

### Attack rolls
An attack roll is universal regardless of attacker. The source supplies the bonus/penalty, reach/range, damage packet(s), and effects.

Resolution rule:
1. Resolve the universal attack roll.
2. If it misses, normal hit damage is zero unless the source explicitly defines a miss effect.
3. If it hits, resolve all linked damage packets and/or effects through their universal systems.

No monster-specific attack-roll resolver should exist when the ordinary attack mechanic is sufficient.

### Saving throws and checks
A saving throw or check is universal regardless of source. The source supplies the DC, ability, success/failure results, and any linked damage/effects.

A DC 12 Dexterity save and a DC 18 Dexterity save use the same saving-throw mechanic. Only the source parameters differ.

### Advantage and Disadvantage
Advantage and Disadvantage are universal roll modifiers regardless of source. A monster trait, condition, spell, weapon feature, class feature, circumstance, or homebrew rule may grant or impose them, but the engine resolves them through one shared rule.

2024 RAW stacking behavior is universal:
- one or more sources of Advantage still produce only Advantage, not extra d20s
- one or more sources of Disadvantage still produce only Disadvantage
- if at least one source of Advantage and at least one source of Disadvantage apply to the same roll, they cancel and the roll uses one d20 regardless of how many sources exist on either side

The source owns why and when Advantage or Disadvantage applies; the engine owns how the roll is resolved.

### Action economy
Action, Bonus Action, and Reaction are universal action-economy buckets. A source ability declares which bucket it uses; using that ability consumes that bucket through the shared engine.

Default behavior:
- an Action consumes the creature's Action
- a Bonus Action consumes the creature's Bonus Action
- a Reaction consumes the creature's Reaction

An explicit RAW/source rule can override the default when it specifically says so. Specific source text beats the ordinary default, but the override should still be represented as source data feeding the shared action-economy system rather than as source-specific engine code whenever possible.

### Multiattack
Multiattack is one universal attack-sequence mechanic regardless of source.

The source owns:
- the printed/log name
- how many attacks are made
- which attack or ability names are used
- their order, if order matters
- any source-defined alternatives or choices

The engine owns executing the declared sequence through the same universal Action, attack-roll, saving-throw, damage, condition, and effect systems used everywhere else.

Two spear attacks, three claw attacks, one bite plus two claws, or ninety-seven sword attacks are all the same Multiattack mechanic with different source data. Do not create monster-specific Multiattack resolvers when a source-defined sequence is sufficient.

### Recharge and limited availability checks
Recharge is one universal availability-check mechanic. The source declares the die and the accepted result or result set; the engine rolls and decides whether the ability becomes available.

Conceptually:

`roll configured die -> compare result to configured accepted results -> available or unavailable`

Examples:
- RAW `Recharge 5-6`: roll `d6`; results 5 or 6 restore availability.
- Hypothetical homebrew `Recharge 50-500 on d1000`: roll `d1000`; any result from 50 through 500 restores availability.

Recharge answers only whether the named source ability can be used. It does not own that ability's attack roll, save, damage, condition, range, area, or other effects; those remain separate universal mechanics populated by source data.

Likewise, fixed limited uses such as `1/Day`, `3/Day`, or another source-defined count are shared resource counters. The source supplies the count/reset rule; the engine owns availability and consumption.

## Composition rule

A printed ability is a named composition of universal mechanics plus source-owned parameters.

Conceptually:

`SOURCE ABILITY -> attack/save/check/trigger -> universal damage/effects/conditions -> universal defenses and immunities`

The printed name remains for logs and source auditing; it does not create a separate combat subsystem.

## Modularity requirement

Future homebrew monsters and user-created pregens must be able to plug into the same data model without adding code for ordinary mechanics.

If a homebrew ability says `Tail Sweep — DC 15 Strength save or Prone`, it should use the same universal saving-throw and Prone systems already used by SRD monsters and players.

Source-specific code is allowed only when the actual game mechanic is genuinely distinct and cannot be represented by composition of existing universal mechanics.

## Current design test

Before adding code for an ability, ask:
1. What are the actual combat effects?
2. Do those effects already exist as universal mechanics?
3. Can the ability be represented by source data plus composition?
4. Is the only unique part its printed name or numeric parameters?

If yes, do not add a source-specific mechanic.
