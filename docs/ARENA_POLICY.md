# Iron Pit Arena Policy

Iron Pit is a rules-first card-vs-card deathmatch. It intentionally simplifies battlefield geometry while preserving the D&D 2024 / SRD 5.2.1 combat rules that decide the fight.

## Locked standard arena assumptions

- Every fight continues until one side is dead. There is no morale, surrender, fleeing, retreat, or kiting AI.
- The standard arena is flat and unobstructed. Terrain-only movement modes do not matter unless a future arena explicitly enables that terrain.
- The standard arena has sufficient diffuse or artificial illumination but is not in direct sunlight. Features that specifically require sunlight are inactive unless a future arena explicitly enables sunlight.
- Because the standard arena is unobstructed and combatants never retreat, Hide is not a legal tactical option and voluntary Disengage-to-retreat behavior is not selected. A printed option such as Nimble Escape remains part of the source audit but does not change a standard Pit outcome.
- Combatants always close toward the enemy. Movement away from the enemy is not part of the standard arena policy.
- Ranged and thrown attacks may be used while closing when legal. They are an approach option, not a reason to hold distance.
- Once a combatant reaches melee range, it stays in the brawl. If it has a legal melee attack, that attack is preferred. A truly ranged-only combatant may keep making its ranged attack in melee and takes the normal Disadvantage where the rules require it.
- Melee-only combatants that cannot attack yet may Dodge while using their movement to close. Dodge benefits end if the creature becomes Incapacitated or its Speed is 0, as required by SRD 5.2.1.
- Run-up, charge, leap, pounce, or similar opening-burst tactics are selected only in round 1 when that combatant's initiative total is strictly greater than every enemy's initiative total. A tied total does not qualify even if the arena tie-break puts that combatant first. When the opener qualifies, the Pit assumes any required pre-contact run-up happened immediately before the cards reached their starting slots, so starting adjacent does not erase the opener. Any remaining movement needed to reach the target still has to be legal. Printed target-size, attack, damage, save, and condition effects still resolve normally; the policy never invents an extra attack or extra damage. If the opener is unavailable, the combatant uses normal melee/ranged behavior from its board slot.
- A creature can use a printed Fly speed as horizontal closing movement in the open Pit, but it does not voluntarily gain altitude, leave melee, or kite. Consequently, Flyby does not alter standard-Pit tactics unless a future arena allows voluntary disengagement movement.
- Pushback or other forced movement may create distance, but on its next turn a combatant closes again rather than exploiting that distance to kite.
- If a side has at least two active combatants, ally-within-5-feet requirements are treated as satisfied under the flat-pit abstraction. Downed, unconscious, or dead allies do not count.
- Standing enemies are targeted before downed enemies. If no standing enemy remains, living unconscious or stable player characters remain valid targets so the deathmatch can reach a rules-resolved death rather than ending merely at 0 HP.
- Standard monsters die at 0 HP. Player characters use the supported zero-HP, Unconscious, Death Saving Throw, massive-damage, and damage-while-at-0 rules until they die or regain HP.
- Unconscious player characters are also Incapacitated and Prone. Attack rolls against them have Advantage; hits from attackers within 5 feet are Critical Hits; and when Unconscious ends they remain Prone until they stand normally.
- Iron Pit has no Short Rest or Long Rest during a fight. Each limited-use combat resource begins with the exact uses granted by that combatant's class, species, level, or printed stat block. Once spent, a use remains spent for the rest of the fight. Ending an effect, dropping to 0 HP, stabilizing, or regaining HP never refunds or refreshes that resource.
- Effects end only when their own rules say they end. Becoming Incapacitated can end effects such as Rage or Dodge when their printed rules require it, but it does not erase unrelated conditions or restore spent resources. Healing above 0 HP does not reactivate an effect that ended.
- Multiple sources of Advantage never become more than Advantage. Multiple sources of Disadvantage never become worse than Disadvantage. If any Advantage and any Disadvantage both apply, the d20 roll is normal regardless of how many sources exist on either side.
- The same named condition is not multiplied into stronger copies merely because multiple sources apply it. Each source still matters for its own duration and removal rules where RAW requires that distinction.

## Readiness rule

A stat-block feature does not block standard-arena readiness when these arena assumptions make that feature unable to affect the fight. A missing attack, damage rider, defense, saving throw, condition, resource, reaction, spell, recharge feature, or other mechanic that can change the combat outcome still blocks readiness.

Every runnable pregen must independently reconcile its combat-relevant class, species, feat, equipment, resource, and level-scaling rules. Every runnable monster must reconcile every combat-relevant printed stat-block mechanic. If a scaling rule or outcome-changing mechanic has not been independently certified, the card remains blocked.

These are explicit Iron Pit arena assumptions, not changes to a creature's printed statistics. Unsupported outcome-changing mechanics fail closed instead of being approximated.
