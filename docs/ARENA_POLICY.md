# Iron Pit Arena Policy

Iron Pit is a deterministic card-vs-card D&D 2024 / SRD 5.2.1 combat-math simulator. It is not a virtual tabletop and does not attempt to reproduce battlefield mechanics that cannot change the simplified Pit result.

`docs/IRON_PIT_DAMAGE_SCOPE.md` and `docs/IRON_PIT_COMBAT_LOOP.md` are authoritative when older implementation behavior conflicts with this policy.

## Universal combatant rule

Heroes and monsters use one combat engine. Strength, Armor Class, Initiative, attack rolls, saving throws, Advantage/Disadvantage, damage, healing, resources, resistances, and other supported mechanics mean the same thing regardless of which kind of card owns them.

A card is an immutable source definition. Starting a fight creates disposable runtime state. Buffs, debuffs, current HP, Temporary HP, spent resources, active effects, and other fight-only values may change during combat, but combat must never write those changes back into the source card. A new fight begins from the source definition again.

## Combat-math gate

A printed effect is in scope only when it changes the probability, amount, frequency, timing, legality, prevention, or recovery of damage/HP in the Iron Pit loop.

Examples of in-scope consequences include:

- Advantage or Disadvantage on an attack that can deal damage;
- an AC, attack, save, save-DC, damage, resistance, immunity, vulnerability, healing, Temporary HP, or regeneration change;
- gaining or losing an Action, Bonus Action, Reaction, Multiattack, Extra Attack, Legendary Action, spell slot, recharge use, or other resource when that changes legal damage/healing frequency;
- recurring damage or an effect that prevents a damaging action;
- a range or reach requirement only when it determines whether the selected damaging action can legally occur in the standard Pit abstraction.

Out-of-scope consequences include movement-only speed changes, forced movement with no Pit combat consequence, terrain, object interaction, dropped-item position, exploration, social effects, narrative effects, and conditions whose only consequence is state the Pit does not use.

A feature name never determines scope. Its mathematical consequence does. If that consequence is genuinely ambiguous, stop that mechanic and ask the user rather than expanding the simulator by assumption.

## Standard arena assumptions

- Every fight continues until one side is dead. There is no morale, surrender, voluntary retreat, or kiting AI.
- The arena is flat and unobstructed. Terrain-only rules are ignored unless a future arena explicitly activates them.
- There is sufficient ordinary illumination and no direct-sunlight assumption unless a future arena explicitly says otherwise.
- There is no public starting-distance selector.
- Melee/frontline combatants begin effectively engaged with the opposing frontline. Ranged combatants and casters are stacked immediately behind their frontline.
- Ordinary movement rate is not simulated and does not affect certification. Walk, Fly, Swim, Burrow, and Climb values remain source metadata but do not change normal Pit attack availability merely because one creature is faster or slower than another.
- A source creature with no usable movement mode at all may be deferred as a content-eligibility edge case. A temporary runtime Speed of 0 never removes a combatant from a fight and never changes roster eligibility.
- Movement-only Speed changes, dragging, pushing, pulling, retreating, kiting, and pathfinding are ignored unless the effect itself deals damage or changes another supported combat-math consequence.
- Run-up, Charge, Pounce, leap, and similar opening-burst features are considered in round 1 when the combatant wins initiative as required by the locked combat-loop policy. Their printed attack, damage, save, target, size, and resource requirements still apply. The Pit never invents extra damage.
- Ranged/thrown/spell attacks are used when legal. A ranged-only combatant may continue its legal ranged routine and receives any in-scope attack-math penalty that applies.
- Ally-dependent mechanics require a real legal ally. Iron Pit never invents a nearby ally solely to activate a feature.
- Standing enemies are targeted before downed enemies. If no standing enemy remains, living unconscious/stable characters remain valid targets so the deathmatch can resolve to death.
- Standard monsters die at 0 HP. Player characters use the supported zero-HP/death-save rules because those rules change survival math.
- No Short Rest or Long Rest occurs during a fight. Limited resources begin at their source-defined maximum and remain spent for that runtime fight unless their own in-combat recharge rule restores them.
- Multiple sources of Advantage remain Advantage; multiple sources of Disadvantage remain Disadvantage; any amount of each cancels to a normal d20 roll.

## Grappled in Iron Pit

Grappled remains a real combat condition because its attack restriction changes combat probability.

- A Grappled combatant attacks a creature that is currently grappling it with a normal attack roll, absent other Advantage/Disadvantage sources.
- A Grappled combatant has Disadvantage on attack rolls against creatures other than its grappler.
- The printed Speed 0 consequence is retained as runtime condition state where needed by shared rules, but Iron Pit ignores it for movement and roster eligibility.
- Dragging or repositioning a Grappled target is ignored unless a future supported mechanic gives that repositioning a direct combat-math consequence.
- Grapple-dependent attacks, damage, target prerequisites, escape DCs, and Grappled-plus-Restrained effects remain modeled when they change attack, damage, action, or survival math.
- A grapple ends when its grappler is no longer a legal source, such as when the grappler dies or becomes unconscious.

This is an Iron Pit simplification of battlefield procedure, not a replacement for the shared Advantage/Disadvantage mechanic. The probability effect remains the actual supported d20 mechanic.

## Buffs, debuffs, and temporary effects

Only buffs/debuffs with an in-scope mathematical consequence need runtime representation. Their displayed card state may show the active effect and effective value, but the source value remains unchanged.

Prefer generic temporary modifiers over ability-specific mutation. A feature that grants `+2 AC until the start of the next turn`, for example, should create a generic timed AC modifier; it should not rewrite the card's permanent `armor_class` value.

When an effect expires or combat ends, its runtime modifier disappears. A later fight must not inherit it.

## Caster policy

Casters choose from legal certified damaging/healing/buff options using the combat loop. Damaging spells resolve through the same attack/save/damage primitives used by equivalent monster abilities.

Spell geometry is represented only as far as target count, legal range, friendly-fire avoidance, or another factor changes damage math. Object ignition, terrain alteration, light, visibility, control movement, and similar secondary text are ignored when they cannot change the simplified Pit result.

Spell progression and resource usage remain source-driven. Cantrip scaling is modeled when it changes damage. Upcasting remains deferred unless explicitly reactivated by current project policy.

## Readiness rule

A card is blocked only by an unsupported mechanic that can change Iron Pit combat math under these arena assumptions. Unsupported non-Iron-Pit secondary effects do not block certification.

Every runnable pregen and monster must reconcile the source mechanics that can alter attack/save probability, legal damage/healing frequency, damage amount/type, defenses, HP recovery, resources, or other supported survival math. Equivalent hero and monster mechanics must use the same universal primitive rather than bespoke resolvers.

Unsupported combat-math mechanics fail closed. Unsupported out-of-scope tabletop mechanics are intentionally ignored rather than approximated.
