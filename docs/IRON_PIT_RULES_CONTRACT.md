# Iron Pit Rules Contract — Universal Data-Driven Combat

This file is the highest-authority product and combat contract for D20 Iron Pit. Read it before every combat, monster, pregen, homebrew, certification, or rules-engine change. If code disagrees with this contract, the code is wrong until Chris explicitly changes this contract.

## 1. Product definition

Iron Pit is one automated D&D combat system driven by RAW rules and declarative combatant data.

There is not a player engine, monster engine, pregen engine, PvP engine, or monster-vs-monster engine. Every participant becomes the same compiled combatant and enters the same universal combat engine.

Supported matchups therefore include, without special paths:

- pregen vs monster;
- pregen vs pregen / player vs player;
- monster vs monster;
- official vs homebrew;
- any future imported combatant vs any other legal combatant in the same ruleset.

Names, classes, subclasses, hero IDs, and monster IDs are never combat-rule switches.

## 2. Authoritative pipeline

Source data compiles into one runtime shape:

```text
official/homebrew source
        ↓
edition-scoped JSON data
        ↓
universal capability references
        ↓
compiled combatant
        ↓
fresh mutable fight state
        ↓
ONE universal RAW combat engine
        ↓
canonical events/results
```

Pregens use base identity/build data plus class-level and subclass-level deltas. Monsters use stat-block data. Their authoring inputs may differ, but both MUST compile into the same runtime combatant schema before combat begins.

Python builders and hand-authored per-level snapshots are migration scaffolding, not the target authoring architecture.

## 3. What belongs in combatant JSON

Combatant data describes facts, not implementations. Store the source facts needed to resolve combat, including as applicable:

- edition/ruleset;
- identity and type;
- level/class/subclass or monster metadata;
- ability scores;
- HP, armor/equipment inputs, speed and movement modes;
- proficiency and proficiencies;
- weapons, attacks and action definitions;
- resources and maximum uses;
- spells, slots and spellcasting inputs;
- resistances, vulnerabilities and immunities;
- senses and size/footprint inputs;
- universal capability IDs plus parameters;
- source/audit metadata.

Prefer source inputs over duplicated derived values. Example: store Strength 16 and the relevant proficiency/weapon facts; the shared RAW math derives the +3 Strength modifier and legal attack/damage modifiers. A static ability score remains unchanged until an explicit RAW effect or progression delta changes it.

Do not store a second independently maintained answer when the engine can deterministically derive it from authoritative inputs. Generated snapshots may contain derived values for runtime speed/audit evidence, but they are outputs and must reconcile with source data.

## 4. Universal RAW capability library

Every outcome-changing ability must resolve through a reusable universal capability or primitive.

Examples include attack rolls, damage, saving throws, Advantage/Disadvantage, conditions, Prone, Grappled, healing, Temporary HP, movement, forced movement, Opportunity Attacks, reactions, resources, recharge, spellcasting, concentration, Extra Attack, Multiattack, critical thresholds, Rage, Sneak Attack, Action Surge, Pack Tactics, breath weapons and similar mechanics.

A combatant references capability IDs and parameters. The JSON does not contain a private implementation of the rule.

If two features have the same RAW behavior, they reuse the same primitive even if their names or sources differ. Prone is Prone regardless of whether a spell, weapon, class feature, monster trait, or homebrew combatant caused it.

Before adding a capability, inspect the existing Python and browser engines for an equivalent or composable primitive. Do not duplicate mechanics.

A genuinely new outcome-changing RAW behavior is implemented once in the universal engine, with Python/browser parity and permanent tests, then every qualifying combatant may reference it.

## 5. RAW is the rules foundation

D&D RAW determines what a combatant can do and how the mechanic resolves.

The engine rolls dice, derives modifiers, checks legal actions, resolves abilities and counter-abilities/reactions, applies conditions and defenses, spends resources, tracks timing, and mutates temporary combat state according to the selected edition's RAW.

Never approximate, invent, or silently ignore an outcome-changing RAW rule to make content runnable. Unsupported outcome-changing mechanics fail closed.

Noncombat-only features may be retained as source metadata without runtime implementation when they cannot alter an Iron Pit fight.

## 6. Iron Pit arena policy overlays RAW; it does not replace RAW

Iron Pit rules are environmental and automation-policy constraints applied on top of RAW.

A RAW ability still exists even when the arena makes it strategically useless. The engine/Arena AI knows the arena consequence and chooses another legal option when appropriate.

Example: a creature may RAW possess a summoning ability. If summoned creatures have no combat effect under the Iron Pit arena contract, the ability remains part of the source truth but Arena AI does not waste its action using it when another useful legal option exists.

Arena policy may define environment, target/action selection, survivability, battlefield geometry, and deliberately ignored environmental outcomes. It must never secretly rewrite a creature's printed stats or claim an arena simplification is RAW.

The Pit is magically survivable/hospitable for all creatures. Aquatic biology, atmosphere, breathing requirements, and similar survival constraints do not exclude a combatant. Preserve printed movement modes and speeds.

## 7. Edition isolation

2014 and 2024 source data are separate.

A fight uses one ruleset only. Never mix 2014 and 2024 combatants, spell values, class progressions, monster parameters, or edition-specific feature behavior.

Shared RAW primitives are reused when behavior is genuinely identical. If behavior differs, the capability uses explicit edition-scoped configuration or implementation at the smallest necessary layer.

Common concepts such as attack rolls, damage, Prone, Advantage/Disadvantage and other identical primitives remain universal rather than being needlessly duplicated.

## 8. Pregens and leveling

A pregen is one persistent character progression, not twenty separately authored characters.

Authoritative model:

```text
hero identity/build JSON
+ edition class progression JSON
+ sparse subclass delta JSON
+ equipment/spell/build JSON
→ compiled level N combatant
```

Level N is produced by folding the legal progression from level 1 through N. A level row contains only the changes at that level where practical.

Unchanged state carries forward. Ability scores, race/species, background, equipment, subclass and other persistent facts remain static until RAW progression or an explicit legal build choice changes them.

Derived values are recalculated from the resulting source facts.

Straightforward levels using already-supported capabilities are data work, not new Python builders. Batch all levels for a character/class and let certification identify actual missing universal capabilities.

## 9. Monsters

A monster is declarative stat-block data plus universal capability references.

Adding a monster whose mechanics are already supported should be data + validation + generated certification. Never write a monster-name-specific resolver.

Monster and pregen data MUST converge to the same compiled combatant schema so the universal engine can run any legal pairing.

## 10. Homebrew

Homebrew uses the same schemas and the same universal combat engine.

Homebrew does not bypass engine rules and does not inject arbitrary executable combat behavior. A homebrew monster or character may use existing supported capability IDs and parameters.

If a requested homebrew ability cannot be represented by an existing universal capability, it is unsupported until that ability is deliberately added to the universal capability library. This keeps official and homebrew combat on one auditable engine.

## 11. Immutable source, mutable fight state

Source JSON/cards are immutable during a match.

Starting a fight creates fresh temporary combat state. HP, Temporary HP, conditions, resources, spell slots, concentration, positions, forms, death state and other mutable facts belong to that fight instance.

At match end the instance is discarded. A new fight starts fresh from immutable source data with card-defined resources restored. Mundane ammunition is unlimited unless a more specific Iron Pit rule says otherwise.

## 12. Action selection and counterplay

RAW determines legal actions. Arena policy chooses among legal actions.

The engine must consider abilities, reactions, defenses, counter-abilities, conditions, resources, positioning, range/reach, and other supported facts at their proper timing.

AI selection must not use unavailable abilities, knowingly choose arena-no-effect actions when a useful legal action exists, or bypass RAW action economy.

Dodge is a final legal fallback after supported offensive options cannot be made legal; it is not a way to hide malformed data or unsupported mechanics.

Arena healing selection is a policy overlay, not a RAW rewrite. Healing abilities remain legal whenever the selected edition says they are legal. Arena AI spends a proactive heal only on a Bloodied creature: current HP is half the creature's effective Hit Point maximum or fewer. A living creature at 0 HP is Bloodied. Temporary HP does not change that threshold; Aid and similar current-maximum changes do.

Among legal Bloodied targets, Arena order is:

1. a living ally at 0 HP;
2. a Bloodied ally, lowest current-HP fraction first;
3. Bloodied self, and only for Action or Bonus Action heals.

Second Wind, Lay on Hands, Cure Wounds, Healing Word, Divine Spark heal, Preserve Life, and other proactive heals use this gate. Arena AI does not spend a turn topping off a non-Bloodied combatant.

2014 Survivor is not an Arena choice. It is a RAW start-of-turn heal while the Champion is alive at or below half HP. 2024 Survivor remains unsupported until its distinct Defy Death and Heroic Rally primitives are implemented; Heroic Rally, when added, still uses this Bloodied gate because that is also its printed restriction.

## 13. Battlefield

The battlefield uses one authoritative 5-foot-square grid with real x/y positions.

Printed size determines footprint unless a supported rule changes it. Movement, reach, range, collision, Opportunity Attacks, forced movement, auras, line of sight and area geometry consume the same grid state.

Arena AI may be intentionally simple, but movement legality remains RAW. It should engage rather than kite for no reason, while printed effects and forced movement remain real.

## 14. Engine/runtime parity

Python is the rules-reference and certification oracle. Browser JavaScript is the production fight engine.

A supported capability requires equivalent behavior in both. New mechanics require an explicit parity map, lifecycle/reset behavior, permanent regression tests and audit evidence.

Step, Watch, Replay and Turbo consume the same canonical resolver/event stream. Presentation mode never changes combat rules.

Production combat remains browser-capable without requiring a backend fight resolver.

## 15. Certification

READY is earned, never manually declared.

A combatant/level is runnable only when:

1. source data is legal and schema-valid;
2. it compiles into the universal combatant schema;
3. every outcome-changing capability is supported or explicitly proven arena-irrelevant;
4. derived values reconcile with source inputs;
5. Python/browser parity exists for its mechanics;
6. permanent regression/certification evidence passes;
7. generated artifacts are current;
8. exact-head CI is green.

Generated manifests are outputs, not authoring surfaces.

Batch certification should report unsupported capability IDs and all affected combatants. One blocker must not stop unrelated safe content from being audited.

## 16. Migration/refactor mandate

The repository is being refactored to this architecture.

Preserve working universal mechanics. Replace duplicated hero/monster construction and hand-maintained snapshots with edition-scoped declarative data and shared compilation.

Migration order:

1. lock this contract as authority;
2. define one compiled combatant schema;
3. prove representative pregen and monster inputs compile into it;
4. migrate 2024 Fighter as the first full level-1–20 pregen track and compare against existing certified fingerprints;
5. migrate existing monster data through the same compiled combatant boundary;
6. migrate remaining pregens and monsters in batches;
7. remove obsolete builders/duplicate bookkeeping only after parity tests prove replacement;
8. continuously regenerate certification and capability-yield reports.

Do not continue expanding the obsolete architecture merely to increase counts. New content work must move toward this contract.

## 17. No drift

Before every implementation tranche involving combat, pregens, monsters, homebrew, rules, certification or runtime behavior:

1. read this file;
2. read `AGENTS.md`;
3. identify the source-data/schema impact;
4. identify the universal capability/primitive involved;
5. identify Python and browser resolution points;
6. identify edition scope;
7. identify tests/certification evidence;
8. only then change code/data.

Chat memory, previous summaries, old branches and historical certification counts never override repository authority.

If a requested change conflicts with this file, stop and reconcile the contract first. If RAW interpretation, architecture, mapping, timing, or user intent is uncertain, ask Chris one precise question before implementation.
