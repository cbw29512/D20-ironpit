# Iron Pit Arena Policy

Iron Pit is a rules-first card-vs-card deathmatch. It intentionally simplifies battlefield geometry while preserving the D&D 2024 / SRD 5.2.1 combat rules that decide the fight.

## Locked standard arena assumptions

- Every fight continues until one side is dead. There is no morale, surrender, fleeing, retreat, or kiting AI.
- The standard arena is flat and unobstructed. Terrain-only movement modes do not matter unless a future arena explicitly enables that terrain.
- Combatants always close toward the enemy. Movement away from the enemy is not part of the standard arena policy.
- Ranged and thrown attacks may be used while closing when legal. They are an approach option, not a reason to hold distance.
- Once a combatant reaches melee range, it stays in the brawl. If it has a legal melee attack, that attack is preferred. A truly ranged-only combatant may keep making its ranged attack in melee and takes the normal Disadvantage where the rules require it.
- Melee-only combatants that cannot attack yet may Dodge while using their movement to close. Dodge benefits end if the creature becomes Incapacitated or its Speed is 0, as required by SRD 5.2.1.
- Charge mechanics resolve normally when the required straight-line approach distance is satisfied.
- Pushback or other forced movement may create distance, but on its next turn a combatant closes again rather than exploiting that distance to kite.
- If a side has at least two active combatants, ally-within-5-feet requirements are treated as satisfied under the flat-pit abstraction. Downed, unconscious, or dead allies do not count.
- Standing enemies are targeted before downed enemies. If no standing enemy remains, living unconscious or stable player characters remain valid targets so the deathmatch can reach a rules-resolved death rather than ending merely at 0 HP.
- Standard monsters die at 0 HP. Player characters use the supported zero-HP, Unconscious, Death Saving Throw, massive-damage, and damage-while-at-0 rules until they die or regain HP.
- Unconscious player characters are also Incapacitated and Prone. Attack rolls against them have Advantage; hits from attackers within 5 feet are Critical Hits; and when Unconscious ends they remain Prone until they stand normally.

## Readiness rule

A stat-block feature does not block standard-arena readiness when these arena assumptions make that feature unable to affect the fight. A missing attack, damage rider, defense, saving throw, condition, resource, reaction, spell, recharge feature, or other mechanic that can change the combat outcome still blocks readiness.

These are explicit Iron Pit arena assumptions, not changes to a creature's printed statistics. Unsupported outcome-changing mechanics fail closed instead of being approximated.
