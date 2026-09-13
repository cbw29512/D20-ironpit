# Iron Pit Arena Policy

This policy defines universal Iron Pit arena restrictions that apply to monsters and pregens unless explicitly revised by a later product decision.

## Architecture

- Cards/templates remain immutable source data and declare what mechanics a combatant possesses.
- The universal combat engine resolves those mechanics.
- Arena rules are universal policy, never monster-name-specific branches.
- A printed feature that is explicitly arena-disabled or arena-out-of-scope is preserved as source/card information where practical but must not block Iron Pit certification.
- Combat-relevant mechanics that remain in scope must fail closed until universally supported.

## Pocket-dimension combat premise

Iron Pit is a pocket dimension built specifically for combat. Combatants enter to fight, cannot leave the arena by supernatural or planar means, and are completely restored after the match. The arena is not an adventuring environment.

## Arena-disabled mechanics

These mechanics do not function in Iron Pit and must not block certification:

- Lair actions and regional effects.
- Summoning, spawning, splitting, duplicates, animated reinforcements, or any other creation of additional combatants during a match.
- Burrowing.
- Teleportation, Misty Step-style relocation, Dimension Door-style relocation, Plane Shift, planar travel, ethereal escape, phasing through arena boundaries, Banishment-style removal, and other supernatural travel that relocates a combatant outside normal arena movement.
- Fleeing, surrender, morale retreat, or escape from the arena.
- Siege/object-damage mechanics and destructible terrain. Nothing in the Iron Pit is destructible unless a later explicit arena rule adds such an object.
- Worn or carried equipment is indestructible and cannot be permanently degraded. Rust, corrosion, sunder, permanent AC loss, weapon/shield degradation, and similar equipment-only riders do not function. Direct HP damage and creature-affecting conditions from the same source still resolve normally.
- Delayed consequences whose first meaningful mechanical effect occurs after combat, including delayed disease, infection, aging, curses, or transformations. All combatants are restored after the match.
- Long-duration ritual or noncombat casting that cannot complete meaningfully during an Iron Pit fight.
- Subjective social/deception/illusion behavior that requires adventuring judgment rather than deterministic combat resolution.

## Arena-out-of-scope / noncombat mechanics

These may remain on source cards but do not require runtime combat logic and must not block certification when they cannot change a fight outcome:

- Languages, ordinary telepathy used only for communication, disguises, infiltration, social abilities, lore, exploration features, and similar noncombat utility.
- Generic Search, Help, Ready, Shove, or other improvised tactical actions are not selected by default AI unless a supported printed combat identity or rule specifically requires them.
- Environmental interactions with doors, structures, cliffs, weather, natural water, trees, cover, traps, or similar adventuring terrain. The standard arena remains neutral unless a supported combat effect creates an area or hazard.

## Movement rules

- Normal walking and printed movement speeds remain in scope.
- Flight remains in scope, but altitude can never make a flying combatant permanently unreachable by melee. A flying creature in melee engagement range can be attacked in melee.
- Climb and Spider Climb remain valid movement data, but climbing arena walls cannot create an unreachable or safe-from-melee state.
- Burrow is disabled.
- Forced movement remains in scope. Pushes, pulls, throws, and similar effects stop at the last legal square before an arena wall. Arena walls cause no automatic collision damage unless the printed source explicitly causes damage.
- No movement mode may leave the arena.

## Visibility

- Invisibility is resolved mechanically, not as hidden AI knowledge. Arena AI still knows combatant positions.
- Attacks against an invisible target use the applicable disadvantage and the invisible attacker receives the applicable advantage, subject to normal source-specific exceptions and cancellation rules.
- The AI does not pretend to lose track of an invisible combatant merely to simulate human perception.

## Conditions and control

- Grappled, Restrained, Prone, Stunned, Poisoned, Blinded, Invisible, Petrified, and other deterministic combat conditions remain universal engine mechanics.
- Hard domination, possession, team switching, or command effects that would effectively end automated combat are arena-disabled unless a later explicit Iron Pit control rule replaces them.
- Charm may be represented only through an explicit Iron Pit combat rule; it must not silently become a fight-ending hard-control effect.
- Frightened/fear may not force a combatant to leave the arena. Any Iron Pit-specific fear behavior must remain deterministic and preserve meaningful combat counterplay.

## Transformations and containment

- Polymorph, Shapechange, and other supported transformations modify only the temporary combat instance. The immutable source card never changes.
- Swallow/Engulf remains in scope. The swallowed combatant remains part of combat state, with source-defined damage, conditions, escape rules, and release behavior.

## Turn-effect lifecycle

At the start of every combatant turn, the engine inventories active effects and resolves all effects whose source timing is start-of-turn. Effects explicitly timed for end-of-turn, on-hit, on-damage, source-death, or other windows remain at those exact windows. The universal turn lifecycle must never move a source-defined timing window merely for convenience.

## Healing AI policy

- `bloodied` means current HP is at or below 50% of effective maximum HP.
- Voluntary Action healing is normally not considered until at least one legal intended healing target is bloodied.
- Effective expected healing is capped by missing HP so overheal does not inflate tactical value.
- Healing must be compared against the opportunity cost of the best legal offensive action; the AI must not spend an Action on trivial healing while facing overwhelmingly greater incoming/offensive pressure.
- Critical-health healing receives greater tactical weight than ordinary bloodied healing.
- AoE healing may be considered when at least one legal target is bloodied; incidental effective healing to other affected allies contributes to the total value.
- Bonus Action/reaction healing may use a lower threshold because it does not necessarily replace the primary Action.
- Exact thresholds/multipliers may be tuned globally, but must remain universal AI policy rather than monster-name-specific logic.

## Mechanics intentionally kept in scope

These mechanics materially change Iron Pit outcomes and should remain universal engine capabilities rather than being removed for convenience:

- attacks and Multiattack;
- saving throws and save-based actions;
- damage riders and damage types;
- resistance, immunity, vulnerability, reduction, absorption, and Temporary HP;
- healing and regeneration;
- conditions and ongoing effects;
- forced movement, grapple, restrain, prone, swallow/engulf;
- reactions and projectile interception such as Rock Catching;
- Recharge and limited-use resources;
- AoE geometry and targeting;
- transformations;
- zero-HP/death effects and death-triggered effects;
- Legendary Resistance and Legendary Actions;
- deterministic combat spellcasting.

## Certification rule

For certification purposes, every detected mechanic must fall into one of three buckets:

1. `supported`: implemented by the universal engine and certified in Python/browser parity where required;
2. `arena_disabled` / `arena_out_of_scope`: explicitly neutralized by this policy and therefore not a blocker;
3. `blocked`: combat-relevant in Iron Pit but not yet universally supported.

Do not add monster-name-specific exceptions to move a card between these buckets.
