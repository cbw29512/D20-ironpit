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

## Flat modifiers and bonus-die modifiers

Flat modifiers and bonus-die modifiers are separate runtime channels and may both apply to the same roll or stat-derived check.

For each affected roll channel, such as an attack roll, saving throw, or ability check:

- apply the strongest applicable positive flat modifier;
- apply the strongest applicable negative flat modifier;
- apply the strongest applicable positive bonus-die modifier;
- apply the strongest applicable negative bonus-die modifier;
- additional modifiers within the same channel and sign do not stack;
- flat and die channels do not suppress one another.

Example: an attack with a +2 temporary flat bonus and a +1d4 temporary bonus die uses both. A second +1 flat bonus is suppressed by the +2. A second +1d6 bonus die competes with the +1d4 bonus-die effect; only the strongest applicable positive bonus-die effect is used according to the engine's deterministic comparison rule.

Baseline proficiency, ability modifiers, weapon bonuses, and other permanent construction values remain part of the normal base calculation and are not runtime stacking effects.

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

## Proficiency

Keep proficiency as close to D&D RAW as practical without creating one-off engine complexity.

- Proficiency Bonus is applied once when the combatant is proficient.
- Multiple sources granting proficiency do not stack duplicate Proficiency Bonuses.
- Expertise or double-proficiency effects multiply the normal proficiency contribution rather than adding a second independent proficiency source.
- If an effect genuinely changes the effective Proficiency Bonus, every combat-relevant derived value that uses proficiency must read the current effective value dynamically.
- Do not add exotic proficiency exceptions until a real supported combatant requires them.

## Advantage and Disadvantage

Advantage and Disadvantage are binary and never stack.

- Advantage only: roll 2d20, keep highest.
- Disadvantage only: roll 2d20, keep lowest.
- Both: cancel completely; roll 1d20.
- Multiple sources of Advantage are still one Advantage state.
- Multiple sources of Disadvantage are still one Disadvantage state.

## Action economy and combat flow

Keep the core D&D combat flow RAW unless a deliberate Iron Pit simplification is documented.

- Initiative and turn order remain normal combat concepts.
- A combatant normally has one Action on its turn.
- A combatant can use one Bonus Action when an available feature, spell, or ability permits it.
- A combatant has one Reaction between the starts of its turns, subject to the normal trigger and availability rules.
- Extra Attack changes the number of attacks produced by the Attack action; it is not a separate monster- or class-specific action system.
- Effects such as Action Surge, Incapacitated, Stunned, or reaction denial modify these shared action resources rather than creating bespoke combat flows.
- Movement is the Iron Pit's abstraction and is not simulated as ordinary tactical movement when it has no separate combat-math consequence.

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

## Concentration

Keep Concentration RAW unless a documented simplification is required for implementation.

- A creature can maintain only one Concentration effect at a time, not one per round.
- The same Concentration effect can remain active across many rounds until its duration ends or Concentration is broken.
- Beginning another Concentration effect ends the previous one.
- Taking damage can require a Constitution saving throw to maintain Concentration; failure ends it.
- Incapacitation, unconsciousness, death, or any other RAW Concentration-ending state ends the effect.
- When Concentration ends, every runtime buff, debuff, condition, or other effect owned by that Concentration source is removed immediately.
- Concentration resolution must use the shared saving-throw and runtime-effect systems rather than spell-specific branches.

## Zero HP and death saving throws

Keep death saving throws RAW for combatants that use them.

- A creature that starts its turn at 0 HP and is not Stable makes a Death Saving Throw.
- Roll 1d20 with no ability score attached: 10 or higher is one success; 9 or lower is one failure.
- Three successes make the creature Stable.
- Three failures kill the creature.
- Successes and failures need not be consecutive.
- Regaining any HP or becoming Stable resets both counters to zero.
- A natural 1 on the Death Saving Throw causes two failures.
- A natural 20 on the Death Saving Throw restores 1 HP immediately.
- Taking damage while at 0 HP causes one Death Saving Throw failure.
- If that damage is from a Critical Hit, it causes two failures instead.
- If damage at 0 HP meets the applicable RAW instant-death threshold, the creature dies immediately.
- Zero-HP, Stable, Unconscious, healing, and death-save state must use shared combat state rather than class- or monster-specific branches.

## Conditions and mixed effects

Keep the combat-math portions of conditions and mixed abilities. Ignore only the portions that do not affect Iron Pit outcomes.

The same condition is a universal state regardless of source ability name. Multiple sources may need to remain tracked for duration/source ownership, but the condition's mechanical effect itself is not multiplied.

## Implementation policy

Normalize source abilities into universal primitives such as attack roll, damage packet, saving throw, condition, modifier, Advantage/Disadvantage, resistance/vulnerability/immunity, healing, Temporary HP, action availability, trigger, duration, resource, and target requirement.

Build shared primitives first. Monster records should primarily provide parameters and source names. Exact ability names must remain visible in logs.

Do not reopen these rules monster-by-monster. If a future edge case genuinely conflicts with this policy, stop only for that specific unresolved rule.
