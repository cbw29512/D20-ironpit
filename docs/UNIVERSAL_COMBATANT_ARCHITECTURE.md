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

## Shared-fact rule

Common D&D facts are modeled once and reused everywhere.

Examples:

- HP is HP regardless of creature type.
- AC is AC regardless of whether it came from armor, shield, natural armor, a style, or a temporary modifier.
- ability scores/modifiers and saving throws are shared data.
- weapon properties such as Light are weapon data.
- a weapon's mastery property is weapon data.
- the combatant's selected/known weapon masteries are combatant data.
- action economy, resources, conditions, concentration, damage defenses, movement, attack rolls, and saves are universal mechanics.

A class feature or monster trait should add data or a reusable capability. It should not create a parallel combat engine.

## Weapon Mastery contract

Weapon Mastery activation is universal:

`mastery active = weapon has mastery property AND weapon id is present in combatant.weapon_masteries`

No Fighter, Rogue, Ranger, Barbarian, hero-name, monster-name, or weapon-name branch belongs in the activation check.

The individual mastery handler should contain only its RAW effect and trigger.

Examples:

- Graze: on a miss with an active Graze mastery, deal the attack ability modifier as Graze damage under the audited damage-defense rules.
- Vex: on a qualifying hit with active Vex, grant the next-attack advantage effect against that target.
- Sap: on a qualifying hit with active Sap, apply the next-attack disadvantage effect.
- Nick: when the normal Light-property extra attack is available and Nick mastery is active for the relevant weapon, move that same extra attack into the Attack action instead of spending a Bonus Action. Nick does not create an additional Light extra attack.

The Light-property rule is a shared weapon/action-economy rule. Nick only changes that rule's timing/cost.

## Player-build-first rule

A combat-build overlay is not runnable merely because its metadata exists.

For each hero build:

1. Start with the legal class progression and level facts.
2. Apply legal ability/background/feat choices.
3. Apply equipment, armor, shield, fighting style, weapons, and weapon-masteries selections.
4. Apply class, subclass, species, and spell/resource facts.
5. Compile the resulting definition to the same runtime shape used by monsters.
6. Audit that the compiled runtime actually matches the declared build.
7. Only then may the build be marked active/runnable.

An active build must therefore have an executable compiled combatant, not only a `CombatBuildChoiceOverlay`.

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

A build/creature is runnable only when:

- its authoritative definition is legal/audited;
- the compiler produces the expected runtime data;
- every outcome-changing capability on that runtime is supported or explicitly arena-out-of-scope;
- Python and browser consume the same generated facts;
- permanent tests cover the shared mechanic;
- source-size, generated-static parity, manifests, and exact-head CI pass.

If an overlay says `Nick` but the compiled combatant does not actually have the Light weapon, selected mastery, and runtime data necessary to use it, the build is not active.

## Migration plan

### Phase A — stabilize the contract

- Keep the useful existing shared runtime mechanics.
- Add universal helpers for repeated capability predicates, beginning with Weapon Mastery activation.
- Remove class/name inference where the required fact can be explicit data.
- Keep unsupported mechanics fail-closed.

### Phase B — compile real hero builds

- Make the combat-build overlay an input to actual hero compilation, not metadata only.
- Fighter is the first migration anchor because Great Weapon, Sword-Shield, Archer, and Dual-Wield exercise armor, shield, Fighting Style, weapon properties, masteries, ranged/melee attacks, and action economy.
- Do not duplicate four Fighter progression tables; all builds share one Fighter 1-20 spine and apply only legal build choices.
- Apply the same compiler pattern to the remaining eleven classes.

### Phase C — capability inventory

Generate or derive the complete combat capability inventory from:

- every compiled canonical hero/build/level intended for the product; and
- all 330 SRD monster definitions.

Group missing support by shared mechanic rather than by creature. Implement the highest-yield shared mechanic once, then re-audit all combatants.

### Phase D — simplify orchestration

- Keep turn/AI modules focused on legal choice and sequencing.
- Move feature effects to shared capability modules.
- Delete obsolete hero/monster-specific branches only after equivalent generated/runtime assertions replace them.

## Immediate implementation order

1. Universal Weapon Mastery predicate shared by Graze, Vex, Sap, Nick, and future masteries.
2. Complete weapon facts in declarative schemas (`light`, mastery property, attack ability/modifier where required) and preserve them through compilation/export.
3. Add an executable hero-build compiler contract and make build activation fail closed unless compiled runtime matches the overlay.
4. Migrate Fighter build choices through that compiler.
5. Re-implement/simplify Light + Nick on top of the compiled dual-wield data rather than teaching the turn engine about a Fighter build.
6. Add Two-Weapon Fighting as the small shared damage-modifier rule it actually is.
7. Re-audit Fighter builds, then expand the same compiler to the other classes.
8. Re-audit all 330 monsters after each new shared mechanic.

## Non-negotiable invariants

- RAW outcome-changing rules are never approximated.
- The same mechanic is not reimplemented for different classes or creature types.
- Data is authoritative; names are display text, not rule switches.
- Active means executable and certified.
- Python/browser behavior remains equivalent.
- Permanent CI must execute the cited regression evidence.
- Production source-size limits remain enforced.
- PR #32 remains draft and unmerged until the user explicitly changes that instruction.
