# Universal Combatant Architecture

This is the durable implementation contract for D20 Iron Pit.

## KISS principle

Build the character or monster first. Combat reads that finished creature.

Do not build separate combat systems for classes, subclasses, weapon styles, heroes, or monsters. A combatant is data plus a small set of shared capabilities.

`RAW source -> class/monster data -> subclass specialization -> finished combatant -> shared engine`

## Combatant truth

A finished combatant owns the facts needed by combat:

- ability scores and derived modifiers;
- HP, AC, Speed, initiative, saves, and relevant skills;
- Action, Bonus Action, Reaction, movement, and limited resources;
- armor, shield, weapons, weapon properties, and selected Weapon Masteries;
- Fighting Styles and combat-relevant feats/features;
- spells, spell slots/resources, and spellcasting numbers;
- resistances, vulnerabilities, immunities, conditions, and concentration;
- declared attacks/actions and any other RAW outcome-changing fact.

The engine does not infer rules from a class name, subclass name, hero name, monster name, or display text when the needed fact can be stored directly.

## One universal combat engine

Every normal combatant uses the same baseline:

- one Action;
- one Bonus Action opportunity;
- one Reaction, refreshed at the normal time;
- movement equal to effective Speed.

Features modify that baseline; they do not create another turn engine.

Examples:

- Extra Attack changes the number of attacks in the Attack action.
- Action Surge grants another eligible Action.
- Multiattack is a declared monster action containing its attacks/effects.
- Nick changes the timing/cost of the normal Light extra attack.
- Legendary Resistance changes an eligible failed save into success using a resource.

Saving throws are always shared math:

`d20 + creature save modifier + shared modifiers vs DC`

Attack rolls, ability checks, AC, damage defenses, conditions, concentration, and movement follow the same rule: one resolver, different creature data.

## Class -> subclass -> specialization

A class is built once through the levels before subclass choice.

At the subclass level, each chosen subclass gets one coherent combat specialization that makes sense for that subclass. Do not create several weapon clones inside one subclass just to exercise different weapons.

For a martial/hybrid specialization the data is intentionally small:

- subclass id;
- role;
- ability priority;
- armor and shield;
- primary weapon and a few backups;
- Fighting Style priority when the class grants one;
- Weapon Mastery priority when the class grants mastery;
- optional spell package for hybrids.

The specialization does **not** contain Nick, Graze, Vex, Sap, or similar rule implementations. It only selects weapons/masteries/styles. The weapon catalog and shared mechanics do the rest.

### Fighter target

The 2024 Fighter branches into four Player's Handbook subclasses, with one arena specialization each:

1. **Champion -> two-handed**: Greatsword, Strength, Great Weapon Fighting; Champion's later second Fighting Style is another data choice.
2. **Battle Master -> dual wield**: Shortsword + Scimitar, Dexterity, Two-Weapon Fighting; Vex/Nick come from those weapons when mastered.
3. **Eldritch Knight -> sword and shield**: Longsword + Shield, Strength/Intelligence emphasis, defensive Fighting Style, plus its legal spell package.
4. **Psi Warrior -> ranged**: Longbow, Dexterity/Intelligence emphasis, Archery, and appropriate ranged mastery choices.

The exact equipment/feat/spell choices remain auditable data and may be improved when a more legal/effective option is proven. Changing a loadout must not require a new combat engine.

### Other classes

For every other class:

1. build one base character through levels 1-2;
2. choose three useful, distinct subclasses at level 3;
3. give each subclass one coherent specialization;
4. level each subclass specialization through 20 using the same class progression table plus the subclass's feature table.

Do not invent three artificial variants of the same subclass.

## Weapon specialization contract

Weapon specialization is data.

Example:

```text
Battle Master
primary weapon = Shortsword
secondary weapon = Scimitar
style = Two-Weapon Fighting
mastered weapons include Shortsword and Scimitar
```

The catalog already says:

```text
Shortsword: Light, Finesse, Vex
Scimitar: Light, Finesse, Nick
```

The engine asks only:

`mastery active = weapon has mastery property AND weapon id is in combatant.weapon_masteries`

Then it dispatches the tiny shared handler:

- Graze -> miss effect;
- Vex -> target-scoped next-attack Advantage after the qualifying hit;
- Sap -> next qualifying attack Disadvantage;
- Nick -> move the existing Light extra attack into the Attack action.

No Fighter/Battle Master/Champion/Rogue/Ranger name check belongs in those handlers.

If the weapon or mastery is absent, skip the mastery code path entirely.

## Caster specialization contract

Casters use the same idea, with spell packages doing most of the specialization work.

A caster specialization declares:

- subclass/theme;
- casting ability priority;
- focus/weapon or magic-item slot;
- legal cantrip/spell package;
- optional precombat buff priorities;
- deterministic combat priority.

Examples of useful themes, when supported by the actual subclass/spell list:

- fire-focused damage;
- cold/frost-focused damage/control;
- elemental/generalist damage and control;
- enchantment/mind-control;
- healing/support;
- summoning or battlefield control.

The spell package contains desired spells, but the level compiler exposes only spells the character can legally know/prepare/cast at that level.

Arena AI is deterministic policy, not a new rule system. A simple default is:

1. apply worthwhile legal precombat buffs that fit the arena;
2. prefer the highest-value legal spell the package can currently cast;
3. spend higher-level slots before lower-value attacks when sensible;
4. fall back through the package;
5. use cantrips when appropriate;
6. use a weapon only when spellcasting is unavailable or the weapon is the better legal action.

RAW determines what the caster **can** do. Arena policy determines which legal option it **chooses**.

## Leveling contract

Levels should be data rows, not twenty bespoke implementations.

A class progression row changes only what that level changes, for example:

- proficiency bonus;
- HP from the class Hit Die/Constitution progression;
- resource counts;
- ASI/feat/boon choices;
- Extra Attack count;
- new class features;
- new subclass features;
- new spell slots/spell access;
- new mastery count.

The compiler derives AC, attacks, damage modifiers, saves, spell DCs, resources, and legal actions from the finished level snapshot.

A new level that only changes numbers should normally require no new combat mechanic.

## Combat-relevant-only runtime

Keep full character truth where useful, but do not implement noncombat text in the arena engine unless it can change an Iron Pit outcome.

For every feature:

```text
Can this feature alter an Iron Pit combat result?
NO  -> retain as profile/source data if desired; no runtime combat handler.
YES -> represent the needed fact and use/add one shared mechanic.
```

Arena-out-of-scope is a deliberate product-scope classification, never a substitute for an outcome-changing RAW rule.

## Shared capability pattern

For any new combat mechanic:

1. identify the minimum facts that prove the creature has it;
2. store those facts in character/monster data;
3. add one small generic predicate/handler;
4. call it from the natural shared resolution point;
5. test Python and browser parity;
6. make CI execute that regression permanently;
7. re-audit all heroes and monsters that now meet the same conditions.

Do not begin with class-specific turn logic.

## Monsters

Monsters follow the same model:

`stat block -> declarative combatant -> shared runtime`

If a monster already uses supported mechanics, adding it should mostly be data and certification. A genuinely new outcome-changing trait justifies one new shared handler.

## Certification

A combatant is runnable only when:

- its source data/build is legal and audited;
- the compiled runtime matches the declared creature;
- every combat-relevant capability present on that creature is supported or explicitly arena-out-of-scope;
- Python and browser consume equivalent facts;
- permanent regression evidence exists;
- generated artifacts/manifests match;
- exact-head CI is green.

An incomplete subclass, spell package, weapon property, or feature stays blocked. Never approximate it just to increase the ready count.

## Migration from the older variant model

The older `four Champion variants / three variants per canonical subclass` structure is migration scaffolding, not the target architecture.

Migration order:

1. preserve already-certified shared mechanics;
2. make subclass specialization records authoritative;
3. map Champion to the two-handed Fighter specialization first;
4. add audited Battle Master, Eldritch Knight, and Psi Warrior subclass progression data;
5. compile each Fighter subclass specialization through 20 from the one Fighter class table;
6. retire the old multi-variant Champion files after equivalent tests/certification no longer depend on them;
7. research and select three coherent subclasses for each remaining class;
8. give each one a single weapon/spell specialization record;
9. compile all levels from class + subclass + specialization data;
10. keep reusing the shared mechanics inventory across heroes and monsters.

## Non-negotiable invariants

- KISS: specialization is mostly data.
- Characters and monsters are the source of combat truth.
- Names are not rule switches.
- The same mechanic is implemented once.
- Weapon mastery requires both the weapon mastery property and the combatant's mastery of that weapon.
- Casters receive only spells legal for their level/build.
- Noncombat rules do not bloat the arena engine.
- Unsupported outcome-changing mechanics fail closed.
- Python/browser parity stays mandatory.
- Production source-size limits stay enforced.
- Active means executable and certified.
- PR #32 remains draft and unmerged until explicitly changed.
