# Iron Pit Pregen and Content Rules Contract

This document is a mandatory companion to `docs/IRON_PIT_RULES_CONTRACT.md`. It removes ambiguity about how monsters, pregens, and future homebrew content enter Iron Pit.

## 1. Edition isolation is mandatory

Iron Pit supports two separate D&D rulesets: 2014 and 2024.

- A 2014 fight may use only 2014-legal monsters, pregens, spells, weapons, feats, class features, subclass features, items, and rules.
- A 2024 fight may use only 2024-legal monsters, pregens, spells, weapons, feats, class features, subclass features, items, and rules.
- Never copy a feature, progression, weapon behavior, spell behavior, or combat rule from one edition into the other merely because a class, subclass, monster, or ability shares a name.
- Shared combat concepts may use one universal engine primitive when their actual mechanics are equivalent; edition-specific parameters and behavior remain explicit ruleset data.

## 2. Pregens are real legal characters, not approximate stat blocks

Every pregen must be a legal character under the selected edition's RAW before it can be certified for Iron Pit.

Certification must verify, as applicable:

- legal class and subclass progression at the selected level;
- legal ability scores and derived modifiers;
- legal proficiency bonus;
- legal Armor Class, Hit Points, speed, saves, and skills used by combat;
- legal weapons, armor, shields, spellcasting foci, and combat equipment;
- legal Fighting Style, feats, Ability Score Improvements, and other build choices;
- legal spell lists, prepared/known spells, spell slots, spell attack modifiers, and save DCs;
- legal class and subclass resources and reset timing;
- legal Action, Bonus Action, Reaction, movement, Extra Attack, and other action-economy behavior;
- legal damage dice, modifiers, critical-hit behavior, conditions, saves, concentration, durations, and resource expenditure;
- every combat-relevant class/subclass feature required at that level.

A pregen is not READY merely because its displayed AC, HP, attack bonus, or damage appears plausible. Its combat behavior must be source-derived, edition-correct, and exercised by permanent tests.

## 3. 2014 and 2024 versions of the same pregen are separate builds

The canonical Iron Pit pregen concepts may share names and themes across editions, but each edition owns its own progression and legal loadout.

Examples:

- 2024 Weapon Mastery belongs only to the 2024 ruleset. Mastery properties such as Graze, Nick, Push, Sap, Slow, Vex, Cleave, Topple, or other 2024 mastery behavior must never appear in a 2014 pregen unless an independently legal 2014 rule produces the same effect for another reason.
- 2014 Fighting Styles, feats, subclass progression, spells, and class features use their 2014 wording and levels.
- 2024 Fighting Styles, feats, subclass progression, spells, and class features use their 2024 wording and levels.
- A same-name feature that changed between editions must compile to the correct edition-specific behavior.

## 4. Canonical pregen roster

The canonical twelve pregen concepts are:

1. Berserker Barbarian
2. Lore Bard
3. Life Cleric
4. Land Druid
5. Champion Fighter
6. Open Hand Monk
7. Devotion Paladin
8. Hunter Ranger
9. Thief Rogue
10. Draconic Sorcerer
11. Fiend Warlock
12. Evoker Wizard

Target progression is levels 1 through 10 in both 2014 and 2024. A level is certified independently; one legal level does not imply the rest of the progression is legal.

## 5. One universal combat engine

Monsters and pregens use the same canonical combat resolver. Do not create a separate hero simulator, monster simulator, or edition-specific duplicate engine.

Content compiles into reusable combat primitives such as:

- attacks and damage components;
- saving throws;
- Advantage and Disadvantage;
- conditions and effect lifecycles;
- movement, reach, range, and area geometry;
- Action, Bonus Action, Reaction, and resource spending;
- Extra Attack and Multiattack;
- spell attacks and save-based spells;
- concentration and persistent effects;
- recharge and limited-use resources;
- resistance, immunity, vulnerability, Temporary HP, wards, and healing;
- zero-HP, death, stabilization, and other life states;
- edition-specific weapon behavior, including 2024 Weapon Mastery.

If a needed mechanic is missing, add one reusable primitive whenever possible rather than adding a class-name, hero-name, monster-name, or stat-block-name special case.

## 6. Mandatory content intake pipeline

Every monster and pregen must pass this sequence before public READY status:

1. **Source** — authoritative edition-specific source data exists.
2. **Parse/define** — convert source wording into declarative edition-specific content data.
3. **Classify** — map every combat-relevant rule to an existing universal primitive, an explicit arena-neutral rule, or a genuinely missing primitive.
4. **Compile** — build the immutable combat card/capability definition without cross-edition leakage.
5. **Reference behavior** — prove the Python reference/certification path behaves correctly.
6. **Browser behavior** — prove the production browser engine matches the reference behavior.
7. **Ruleset isolation** — tests prove the content cannot acquire mechanics from the other edition.
8. **Generated artifact parity** — browser registries/manifests match the canonical source definitions.
9. **Permanent regression** — exact behavior is covered by tests.
10. **READY** — only after all required checks pass may the content appear in the public selectable roster.

## 7. Blocker classification

Before writing new engine code, classify a blocked monster or pregen as exactly one of:

- `ENGINE_EXISTS_BINDING_MISSING`
- `ENGINE_EXISTS_CERTIFICATION_MISSING`
- `ARENA_NEUTRAL`
- `ENGINE_TRULY_MISSING`

Audit the existing engine first. `ENGINE_TRULY_MISSING` is the reason to add a new universal mechanic; it is not the default assumption.

If one content entry is blocked, record the blocker and continue with other entries that can be certified. A single monster or pregen must not stall overall roster progress.

## 8. Iron Pit rules versus RAW

RAW governs the selected edition except where `docs/IRON_PIT_RULES_CONTRACT.md` explicitly declares an Iron Pit house rule or arena simplification.

- Never silently change RAW to make automation easier.
- Never silently promote an unsupported rule to READY.
- Never treat an outcome-changing combat rule as flavor-only.
- Iron Pit house rules apply equally through the universal engine to all legal combatants for that ruleset unless the contract explicitly scopes them otherwise.

## 9. Test-ready baseline

The first public dual-edition testing milestone requires at minimum:

- at least 100 certified selectable 2014 monsters;
- at least 100 certified selectable 2024 monsters;
- at least one canonical pregen class/subclass with certified levels 1 through 10 in 2014;
- at least one canonical pregen class/subclass with certified levels 1 through 10 in 2024;
- both editions exercising the same canonical fight resolver and battlefield implementation;
- Step, Watch, Replay, and Turbo consuming the same resolution path where those modes are exposed;
- browser fights proving ruleset isolation and core RAW/Iron-Pit behavior.

The 100-monster threshold is a testing milestone, not completion of either roster.

## 10. Future homebrew

Future 2014 and 2024 homebrew pages must use the same edition-specific intake and capability system.

- 2014 homebrew may select only legal/supported 2014 primitives and parameters.
- 2024 homebrew may select only legal/supported 2024 primitives and parameters.
- Homebrew may combine supported primitives in novel ways, but it must not bypass engine validation, action economy, damage rules, conditions, resource limits, or edition isolation.

Homebrew implementation is deferred until the core Pit and certified pregens/monsters are test-ready.
