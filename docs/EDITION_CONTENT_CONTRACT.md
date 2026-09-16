# Iron Pit Edition Content Contract

This document is a normative companion to `docs/IRON_PIT_RULES_CONTRACT.md`. It removes ambiguity about how monsters, pregens, and later homebrew content enter Iron Pit.

## Hard edition isolation

Iron Pit supports D&D 2014 and D&D 2024 as separate rulesets on one universal combat engine.

- A 2014 fight uses only 2014-legal monsters, pregens, class features, subclass features, feats, spells, weapons, equipment rules, resources, action-economy rules, and other edition-specific mechanics.
- A 2024 fight uses only 2024-legal monsters, pregens, class features, subclass features, feats, spells, weapons, equipment rules, resources, action-economy rules, and other edition-specific mechanics.
- Never copy a mechanic, value, progression level, feature, spell behavior, weapon rule, or stat from one edition into the other merely because the creature, class, subclass, spell, or item has the same name.
- Shared concepts such as attacks, damage, saving throws, Advantage/Disadvantage, conditions, movement, resources, reactions, and timing should use universal engine primitives where their mechanics are genuinely shared.
- Edition differences must be represented explicitly in edition-specific source data, adapters, profiles, or parameters rather than by duplicating the entire combat engine.
- Certification is always edition-specific.

## Pregens are legal characters, not approximations

Every pregen must be a legal build under its selected edition. A pregen is not certified merely because its displayed AC, HP, attack bonus, or damage looks plausible.

Certification must validate all combat-relevant character construction and progression used by Iron Pit, including as applicable:

- class and subclass progression;
- subclass entry level;
- ability scores and derived modifiers;
- proficiency bonus;
- hit points and Hit Dice progression;
- armor, shields, weapons, and equipment legality;
- Fighting Styles and equivalent choices;
- feats and Ability Score Improvements;
- spellcasting ability, known/prepared spells, spell slots, and spell rules;
- class/subclass resources and recharge/recovery rules;
- Extra Attack and other action-economy changes;
- conditions, resistances, immunities, movement, senses, and other combat-relevant features;
- edition-specific weapon systems.

In particular, 2024 Weapon Mastery and its mastery properties belong only to the 2024 ruleset. A 2014 character must not receive Weapon Mastery unless a future explicit Iron Pit house rule changes this contract. Conversely, a 2024 pregen must actually execute its selected mastery properties in combat when RAW makes them relevant; displaying the mastery name without runtime behavior is not certification.

The canonical Iron Pit pregen families are:

- Barbarian — Berserker
- Bard — Lore
- Cleric — Life
- Druid — Land
- Fighter — Champion
- Monk — Open Hand
- Paladin — Devotion
- Ranger — Hunter
- Rogue — Thief
- Sorcerer — Draconic
- Warlock — Fiend
- Wizard — Evoker

The product target is a legal level 1 through level 10 progression for each canonical family in both 2014 and 2024. The two editions may and often will produce different legal builds, features, equipment choices, spell packages, damage curves, and tactical behavior.

## Monster and pregen ingestion pipeline

Monsters and pregens enter the simulator through the same rules-first discipline:

1. Read the pinned source data for the selected edition.
2. Parse or declare the combat-relevant source facts without silently rewriting them.
3. Map those facts to existing universal combat primitives where possible.
4. Apply edition-specific adapters/parameters where RAW differs.
5. If an outcome-changing mechanic is unsupported, fail closed rather than approximating it.
6. If a source rule cannot affect an Iron Pit combat outcome, classify that omission explicitly as arena-neutral/noncombat rather than silently dropping it.
7. Run edition-specific Python/reference tests.
8. Run browser-production parity tests against the same intended behavior.
9. Regenerate derived registries/manifests rather than hand-editing generated output.
10. Mark content READY only after its required capabilities are implemented and the exact source-to-runtime behavior is proven.

A monster or pregen must never become READY solely because it can be displayed or because a fight can start.

## Universal-engine rule

Adding content must not create creature-name, hero-name, or one-off class branches in the combat resolver when the mechanic can be expressed as a reusable capability.

Every blocker should be classified before new engine work begins:

1. `ENGINE_EXISTS_BINDING_MISSING` — bind existing behavior.
2. `ENGINE_EXISTS_CERTIFICATION_MISSING` — complete source/runtime/browser proof.
3. `ARENA_NEUTRAL` — explicitly prove the rule cannot change an Iron Pit outcome.
4. `ENGINE_TRULY_MISSING` — add a reusable primitive, then bind all applicable content.

New universal mechanics must remain usable by monsters, pregens, and future rules-valid homebrew wherever RAW permits.

## Test-build gate

A public testing build may expose an edition only when the exposed content is clearly identified as certified for that edition. For the current Iron Pit playtest milestone, the minimum target is:

- at least 100 certified 2014 monsters;
- at least 100 certified 2024 monsters;
- at least one legal pregen family playable from levels 1 through 10 under 2014 rules;
- at least one legal pregen family playable from levels 1 through 10 under 2024 rules;
- browser combat execution uses the same canonical resolver semantics as certification for all exposed capabilities.

More content may continue to be certified after playtesting begins. Uncertified content must not be presented as certified RAW-complete content.

## Future homebrew

Future homebrew authoring will also be edition-scoped:

- 2014 homebrew may select only mechanics/options legal or explicitly supported within the 2014 Iron Pit rules profile.
- 2024 homebrew may select only mechanics/options legal or explicitly supported within the 2024 Iron Pit rules profile.
- Homebrew composes existing universal capabilities and edition-specific parameters; it does not bypass ruleset validation.

Homebrew UI work is deferred until the core Pit and certified monster/pregen pipelines are stable enough for playtesting.