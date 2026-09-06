# Iron Pit Combat-Math Rules

This file is durable project policy. Treat these rules as locked architecture unless the user explicitly changes them.

## Core scope rule

Iron Pit preserves every D&D effect that changes combat math or action availability and ignores every part of an effect that is purely movement, flavor, exploration, social, or otherwise outcome-neutral inside the Pit.

Examples:

- Prone: keep attack Advantage/Disadvantage consequences; ignore crawling/standing movement costs.
- An effect that only changes Speed: ignore the Speed change.
- An effect that sets Speed to 0, deals 2d6 damage, and causes Prone: ignore Speed 0; keep 2d6 damage and Prone.
- Flavor text such as sweating, smell, speech, appearance, or discomfort is ignored unless it also changes a combat-math result or action availability.
- Iron Pit itself may be treated as magically managing positioning, so combatants do not kite, flee, fly around, burrow around, or otherwise turn combat into a movement simulator.

## Universal-mechanic rule

Ability names do not define engine mechanics. Different source abilities that produce the same mechanical result must reuse the same universal primitive. Preserve the exact source ability name in combat logs.

Example:

- Ghoul `Claw` remains logged as `Claw`.
- Its damage uses the universal attack/damage system.
- Its paralysis rider uses the universal save/condition system.
- Another ability with a different name but the same attack -> damage -> save -> Paralyzed structure must use the same engine path.

Do not create monster-specific resolvers when an existing universal primitive can express the effect.

## Baselines and runtime modifiers

A combatant's legal equipment, permanent bonuses, proficiency, ability scores, and other always-on construction choices are resolved into its starting combat values before combat.

During combat, each modifier channel is evaluated independently.

For a given stat, save, attack modifier, AC modifier, or comparable numeric channel:

- apply the strongest applicable positive runtime modifier;
- apply the strongest applicable negative runtime modifier;
- additional positive modifiers to that same channel do not stack;
- additional negative modifiers to that same channel do not stack;
- modifiers to different channels apply normally at the same time.

Conceptually:

`effective = base + strongest_positive + strongest_negative`

Example: +4 Strength and +3 Dexterity both apply because they affect different stats. +4 Strength and +2 Strength do not stack; use +4 Strength.

## Dynamic derived-stat recomputation

Runtime ability-score buffs and debuffs modify the effective ability score first. Every derived combat value must read that current effective score rather than a cached starting modifier.

Example:

- Strength 18 has a +4 modifier.
- A +4 Strength runtime buff produces effective Strength 22 and therefore a +6 modifier.
- Strength-based attack rolls, Strength-based damage, Strength saving throws, and any other combat-relevant Strength-derived calculation immediately use +6 instead of +4.
- When the buff expires, those derived values immediately return to the values produced by the unmodified score.
- Negative ability-score effects work the same way in reverse.

This evaluation is dynamic throughout combat. At minimum, active effects are reconciled each round and whenever an effect is applied, expires, is removed, suppressed, or replaced. Do not permanently mutate the source combatant definition.

The same rule applies to Dexterity, Constitution, Intelligence, Wisdom, and Charisma. If an affected ability is used for a spell attack, spell save DC, saving throw, attack, damage, or another modeled combat calculation, the derived value must use the current effective ability score.

## Advantage and Disadvantage

Advantage and Disadvantage are binary and never stack.

- Advantage only: roll 2d20, keep highest.
- Disadvantage only: roll 2d20, keep lowest.
- Both: cancel completely; roll 1d20.
- Multiple sources of Advantage are still one Advantage state.
- Multiple sources of Disadvantage are still one Disadvantage state.

## Damage packets

Damage is not governed by the strongest-positive/strongest-negative modifier rule. Legitimate damage components stack and must remain typed separately.

Example:

- 1d6 slashing
- +1d4 fire
- +1d6 cold
- +2d4 lightning
- +13 Strength-based flat damage where applicable

All legitimate components are rolled and resolved. Each damage type is processed independently for defenses before the final received damage total is summed.

## Critical hits

Critical hits are tied to attack rolls, not to the weapon-versus-spell distinction.

- An attack-roll weapon attack can crit.
- An attack-roll spell attack can crit.
- A save-based effect does not crit.
- On a critical hit, double all eligible damage dice that belong to that attack.
- Do not double flat modifiers.
- A separate save-based rider after the hit is resolved separately and is not automatically doubled by the critical hit unless the source rule explicitly makes those dice part of the attack's critical damage.

## Resistance, Vulnerability, and Immunity

Resolve each typed damage component independently.

- normal: x1
- resistance: x0.5
- vulnerability: x2
- resistance + vulnerability to the same damage type: cancel to x1
- immunity: 0 damage and overrides resistance/vulnerability for that damage type

Duplicate resistance does not stack. Duplicate vulnerability does not stack.

## Temporary Hit Points

Temporary Hit Points never stack. Keep the highest currently applicable Temporary HP amount.

## Healing

Healing follows normal D&D behavior: current HP cannot be healed above current maximum HP.

If maximum HP is currently reduced, healing is capped by the current reduced maximum.

## Conditions and mixed effects

Keep the combat-math portions of conditions and mixed abilities. Ignore only the portions that do not affect Iron Pit outcomes.

The same condition is a universal state regardless of source ability name. Multiple sources may need to remain tracked for duration/source ownership, but the condition's mechanical effect itself is not multiplied.

## Implementation policy

Normalize source abilities into universal primitives such as attack roll, damage packet, saving throw, condition, modifier, Advantage/Disadvantage, resistance/vulnerability/immunity, healing, Temporary HP, action availability, trigger, duration, resource, and target requirement.

Build shared primitives first. Monster records should primarily provide parameters and source names. Exact ability names must remain visible in logs.

Do not reopen these rules monster-by-monster. If a future edge case genuinely conflicts with this policy, stop only for that specific unresolved rule.
