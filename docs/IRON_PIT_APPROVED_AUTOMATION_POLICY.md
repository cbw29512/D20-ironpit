# Iron Pit Approved Automation Policy

This file records explicit product decisions approved by Chris for automated Iron Pit combat. These decisions constrain AI policy and capability design and must be applied consistently across Python, browser, Step, Watch, Replay, and Turbo. They do not override RAW legality; they decide among legal options and define arena/product scope.

## 1. Beneficial monster abilities are used automatically

When a monster has a legal and useful reaction, Bonus Action, Recharge ability, limited-use ability, regeneration effect, aura, spell, or similar combat feature, the automated policy should use it when the engine determines it improves the monster's combat position. The simulator must not stop to ask the player which legal monster option to choose.

## 2. Environmental requirements do not block combat

The magical Iron Pit remains hospitable to all creatures. Aquatic, flying, burrowing, climbing, breathing, atmosphere, sunlight/environment, habitat, and similar environmental requirements do not prevent a creature from participating. This does not grant free movement or suppress combat effects that are actually created by a supported ability during the fight.

## 3. Preserve combat-relevant RAW; omit only outcome-irrelevant story effects

Damage, conditions, healing, regeneration, maximum-HP changes, attachment, curses, auras, reactions, forced movement, legendary mechanics, resource use, and other outcome-changing combat effects remain modeled according to source rules. Story-only consequences that cannot alter the current Iron Pit combat may be omitted from runtime.

## 4. AI chooses the strongest useful legal option

When several legal attacks, actions, spells, or abilities are available, the automated policy chooses the strongest useful combat option under the existing legality-first policy. It should not randomly choose an obviously inferior option merely because it is legal. Hidden enemy statistics must not be used unless legitimately known during the fight.

## 5. Limited resources are meant to be spent

Because every fight resets runtime state, monster AI should use X/Day abilities, Recharge abilities, spell slots, charges, and similar finite combat resources when they are legal and useful rather than conserving them for a hypothetical later encounter. It must still avoid knowingly wasting them on illegal or meaningless targets.

## 6. Spawn/summon/split mechanics remain in scope

Abilities that create additional combatants are not banned or approximated away. They should use one universal spawn/combatant-creation architecture supporting independent entities, HP, actions, saves, conditions, initiative/control rules, cleanup, and source-specific limits. Splitting, summoned creatures, created undead, and similar mechanics should bind to that shared primitive rather than creature-name-specific code.

## Implementation rule

Before adding a new monster mechanic, first check whether an equivalent universal mechanic already exists. Reuse it when equivalent. If none exists, implement the missing universal primitive once, prove Python/browser parity, then bind every matching monster that can be represented by it. Never add monster-name-specific combat-resolution branches merely to increase the certification count.
