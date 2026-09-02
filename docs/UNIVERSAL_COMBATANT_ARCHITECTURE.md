# Universal Combatant Architecture

This document is the durable implementation plan for D20 Iron Pit combat architecture. It applies to heroes, monsters, generated browser data, Python reference behavior, certification, and future combat capabilities.

## Core principle

Build the combatant first. Resolve mechanics second.

A hero or monster is primarily data:

- identity, class/level or monster source identity;
- ability scores and derived modifiers;
- Armor Class, Hit Points, Speed, initiative, saves, and relevant skills;
- equipment and weapon properties;
- attacks and damage profiles;
- weapon masteries actually known by that combatant;
- fighting styles, feats, class/subclass/species traits, monster traits;
- resources and limited uses;
- spells and spell resources;
- resistances, vulnerabilities, immunities, and conditions;
- action, Bonus Action, Reaction, and other timing facts required by RAW.

The engine must not infer a combat feature from a class name, hero name, monster name, or weapon name when the same fact can be declared explicitly in combatant data.

## Required pipeline

`RAW source -> legal hero build / monster stat block -> declarative combatant definition -> universal compiler -> CombatantTemplate -> generic combat engine -> generated browser parity -> certification`

Heroes and monsters converge on the same `CombatantTemplate` before combat begins. Once combat begins, shared RAW mechanics operate on combatant state and declared capabilities rather than on hero-vs-monster special cases.

## Universal turn economy

Every normal combatant begins a turn from the same action-economy baseline:

- one Action;
- one Bonus Action opportunity;
- one Reaction availability, refreshed at the start of the creature's turn;
- movement equal to its currently effective Speed.

A feature does not create a different turn engine. It only modifies this baseline.

Examples:

- Extra Attack changes how many attacks the Attack action contains.
- Action Surge grants an additional Action under its printed restrictions.
- a monster Multiattack is one declared action containing its listed attacks/effects.
- Nick changes the timing/cost of the existing Light-property extra attack.
- a Bonus Action feature consumes the same universal Bonus Action resource.
- a Reaction feature consumes the same universal Reaction resource.

## Universal d20/save math

Saving throws are shared math, not creature-specific code:

`d20 + creature's save modifier + applicable shared modifiers vs effect DC`

For characters, the save modifier should be derived from the character's ability scores, proficiency bonus, and save proficiencies wherever practical. Monster definitions may preserve printed stat-block save bonuses when the source explicitly supplies them.

Features that alter a failed save act after the shared save result. For example, Legendary Resistance is a limited resource that changes an eligible failed saving throw into a success; it is not a second saving-throw engine.

Attack rolls, ability checks, spell save DCs, and other d20 math follow the same principle: store authoritative creature facts and run one shared resolver.

## Shared-fact rule

Common D&D facts are modeled once and reused everywhere.

Examples:

- HP is HP regardless of creature type.
- AC is AC regardless of whether it came from armor, shield, natural armor, a style, or a temporary modifier.
- ability scores/modifiers and saving throws are shared data.
- weapon properties such as Light, Finesse, Two-Handed, and Versatile are weapon data.
- a weapon's mastery property is weapon data.
- the combatant's selected/known weapon masteries are combatant data.
- action economy, resources, conditions, concentration, damage defenses, movement, attack rolls, and saves are universal mechanics.

A class feature or monster trait should add data or a reusable capability. It should not create a parallel combat engine.

## Weapon Mastery contract

Weapon Mastery activation is universal:

`mastery active = weapon has mastery property AND weapon id is present in combatant.weapon_masteries`

No Fighter, Rogue, Ranger, Barbarian, hero-name, monster-name, or weapon-name branch belongs in the activation check.

The individual mastery handler contains only its RAW effect and trigger.

Examples:

- Graze: on a miss with an active Graze mastery, deal the attack ability modifier as Graze damage under the audited damage-defense rules.
- Vex: on a qualifying hit with active Vex, grant the next-attack advantage effect against that target.
- Sap: on a qualifying hit with active Sap, apply the next-attack disadvantage effect.
- Nick: when the normal Light-property extra attack is available and Nick mastery is active for the relevant weapon, move that same extra attack into the Attack action instead of spending a Bonus Action. Nick does not create an additional Light extra attack.

The Light-property rule is a shared weapon/action-economy rule. Nick only changes that rule's timing/cost.

## Hero progression and optimized clone families

Each class begins with one persistent named base character identity. Build and level that same character instead of creating unrelated pregens at every level.

- Levels 1-2 are the shared base-class character.
- At level 3 the class takes its canonical audited subclass.
- From that point, generate optimized variants that remain the same character/class/subclass progression but make legal build choices appropriate to a different combat role, weapon package, spell emphasis, or equipment package.
- "Clone" means a derived variant, not a byte-for-byte copy: class/subclass features remain shared, while ability advancement, fighting style, weapon mastery choices, equipment, feats, prepared/known spells, and similar legal selections may differ when optimization requires it.
- Do not duplicate the class/subclass progression logic for each variant. Apply a small variant overlay to the shared progression.

### Variant counts

- Fighter: four optimized variants.
- Every other core class: three optimized variants.
- The current build registry already has this exact shape: 37 named variants total (4 Fighter + 3 × 11 other classes).

### Fighter Champion family

Karnok Stoneward follows one Fighter progression through level 3, takes Champion, then produces four optimized Champion variants that each continue to level 20:

1. **Dual Wield** — Dexterity-first Light weapon package; uses shared Light/Nick/Vex/Two-Weapon Fighting rules only when the compiled character actually has those facts.
2. **Two-Handed** — Strength-first two-handed weapon package; the current internal `great-weapon` build id represents this variant during migration.
3. **Sword and Shield** — one-handed weapon + Shield with a defensively sensible Fighting Style/mastery package.
4. **Ranged** — Dexterity-first ranged weapon package with Archery and appropriate ranged masteries.

All four variants share Fighter and Champion progression. Optimization may change legal ASI/feat choices, weapon masteries, fighting-style selections, and equipment where appropriate to the weapon package.

### Other class families

For each of the other eleven classes:

1. build the named base character through levels 1-2;
2. apply the class's canonical audited subclass at level 3;
3. generate three optimized variants from that same class/subclass character;
4. continue each variant through level 20 using the same shared class/subclass feature progression plus small optimization overlays.

A caster variant may differ mainly by spell selection or combat role rather than by weapon. A martial/hybrid variant may differ by weapon, fighting style, feat/ASI path, armor/shield choice, or spell package. The optimization must remain RAW and legal at the level where the choice is made.

## Player-build-first rule

A combat-build overlay is not runnable merely because its metadata exists.

For each hero variant:

1. Start with the legal base character progression.
2. Apply the canonical subclass at the legal level.
3. Apply the chosen optimization overlay (abilities/ASIs, equipment, armor, shield, fighting style, weapons, masteries, feats, spells, and other legal choices).
4. Derive HP, AC, initiative, attack bonuses, damage modifiers, save bonuses, skill bonuses, spell DCs, resources, and action options from the resulting character facts.
5. Compile the resulting definition to the same runtime shape used by monsters.
6. Audit that the compiled runtime actually matches the declared variant.
7. Only then may the variant be marked active/runnable.

An active variant must therefore have an executable compiled combatant, not only metadata.

## Monster rule

Monster onboarding remains data-first:

`SRD source -> declarative combatant definition -> universal compiler -> shared runtime`

If a monster uses an already-supported mechanic, onboarding should normally be data plus certification. New resolver code is justified only when the source introduces a genuinely new outcome-changing RAW mechanic.

## Turn-engine boundary

The turn engine chooses and sequences legal actions. It must not contain class-feature implementations.

Good responsibilities for turn/AI code:

- choose a legal target;
- choose a legal attack/action from the combatant's compiled options;
- spend movement/action resources through shared action-economy services;
- invoke a shared attack/action resolver;
- apply deterministic arena policy where a tactical choice is required.

Bad responsibilities for turn/AI code:

- checking `class_id == fighter`;
- checking a hero/monster name to grant a feature;
- implementing Graze/Vex/Sap/Nick directly;
- inventing an extra attack because a particular build is expected to dual wield;
- duplicating the same RAW mechanic separately for heroes and monsters.

## Capability implementation pattern

For a new mechanic:

1. Identify the minimal authoritative data needed to know whether the capability exists.
2. Add that data to the shared schema/compiler if it is not already represented.
3. Write one small reusable predicate/handler for the RAW trigger/effect.
4. Call it from the generic resolution point where that trigger naturally occurs.
5. Add Python and browser parity tests.
6. Add permanent CI coverage.
7. Re-audit all heroes and all 330 monsters for newly unlocked definitions.

Do not begin by writing class-specific or monster-specific combat branches.

## Certification contract

Certification must prove the compiled creature, not declarations in isolation.

A variant/creature is runnable only when:

- its authoritative definition is legal/audited;
- the compiler produces the expected runtime data;
- every outcome-changing capability on that runtime is supported or explicitly arena-out-of-scope;
- Python and browser consume the same generated facts;
- permanent tests cover the shared mechanic;
- source-size, generated-static parity, manifests, and exact-head CI pass.

If an overlay says `Nick` but the compiled combatant does not actually have the Light weapon, selected mastery, and runtime data necessary to use it, the variant is not active.

## Migration plan

### Phase A — stabilize the contract

- Keep useful existing shared runtime mechanics.
- Centralize repeated capability predicates, beginning with Weapon Mastery activation.
- Make base Action/Bonus Action/Reaction and d20/save math explicitly universal.
- Remove class/name inference where the required fact can be explicit data.
- Keep unsupported mechanics fail-closed.

### Phase B — compile real hero variants

- Make the build overlay an input to actual hero compilation, not metadata only.
- Fighter Champion is the first migration anchor because its four variants exercise armor, shield, Fighting Style, weapon properties, masteries, ranged/melee attacks, and action economy.
- Build one Fighter/Champion progression and apply four optimized variant overlays rather than four progression tables.
- Apply the same base character -> canonical subclass -> three optimized variants pattern to each remaining class.

### Phase C — capability inventory

Generate or derive the complete combat capability inventory from:

- every compiled canonical hero/variant/level intended for the product; and
- all 330 SRD monster definitions.

Group missing support by shared mechanic rather than by creature. Implement the highest-yield shared mechanic once, then re-audit all combatants.

### Phase D — simplify orchestration

- Keep turn/AI modules focused on legal choice and sequencing.
- Move feature effects to shared capability modules.
- Delete obsolete hero/monster-specific branches only after equivalent generated/runtime assertions replace them.

## Immediate implementation order

1. Universal Weapon Mastery predicate shared by Graze, Vex, Sap, Nick, and future masteries.
2. Complete weapon facts in declarative schemas (`light`, `finesse`, `two_handed`, `versatile`, mastery property, attack ability/modifier where required) and preserve them through compilation/export.
3. Make universal Action/Bonus Action/Reaction and save-math contracts explicit in tests and data.
4. Add an executable hero-variant compiler contract and make activation fail closed unless compiled runtime matches the variant overlay.
5. Migrate Fighter Champion's four optimized variants through that compiler and level each to 20.
6. Re-implement/simplify Light + Nick on top of the compiled dual-wield data rather than teaching the turn engine about a Fighter build.
7. Add Two-Weapon Fighting as the small shared damage-modifier rule it actually is.
8. Re-audit all four Fighter Champion variants.
9. Repeat the same compiler pattern for the other eleven classes, three optimized variants each.
10. Re-audit all 330 monsters after each new shared mechanic.

## Non-negotiable invariants

- RAW outcome-changing rules are never approximated.
- The same mechanic is not reimplemented for different classes or creature types.
- Data is authoritative; names are display text, not rule switches.
- Active means executable and certified.
- Python/browser behavior remains equivalent.
- Permanent CI must execute the cited regression evidence.
- Production source-size limits remain enforced.
- PR #32 remains draft and unmerged until the user explicitly changes that instruction.
