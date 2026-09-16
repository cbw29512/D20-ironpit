# Iron Pit Pregen Edition Rules Contract

This file is an authoritative companion to `docs/IRON_PIT_RULES_CONTRACT.md` for pregen content and the content-ingestion pipeline. If code, generated data, UI behavior, certification metadata, or historical documentation conflicts with this contract, the implementation must be corrected or this contract must be explicitly revised.

## 1. Hard edition isolation

- 2014 pregens must be legal D&D 5e 2014 characters and may use only 2014 class, subclass, species/race, feat, spell, equipment, weapon, action-economy, resource, and advancement rules.
- 2024 pregens must be legal D&D 2024 characters and may use only 2024 class, subclass, species/background/origin-feat, feat, spell, equipment, weapon, action-economy, resource, and advancement rules.
- A 2014 fight may load only 2014 monsters and 2014 pregens.
- A 2024 fight may load only 2024 monsters and 2024 pregens.
- Never infer that same-name classes, subclasses, features, spells, or weapons are mechanically identical across editions.
- Shared mechanics use the universal engine; edition differences remain explicit declarative data or ruleset-scoped behavior.

## 2. Canonical pregen roster

The canonical core-class test roster is:

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

Each canonical hero must have a separately legal 2014 progression and 2024 progression. Similar identity does not require identical stats, equipment, feature timing, spell selection, or tactics.

## 3. Level progression and legality

- Each edition-specific canonical hero progresses level-by-level from level 1 through level 20.
- A level derives from the prior certified level plus that edition's legal advancement delta.
- Only certified levels are runnable in the public/test Pit.
- Combat-relevant class, subclass, race/species, background/origin, feat, equipment, spell, resource, and feature rules must be represented accurately or remain explicit blockers.
- Ability scores, ASIs/feats, fighting styles, invocations, metamagic, subclass selections, spell choices, and equipment choices must satisfy the selected edition's prerequisites and level gates.

## 4. Weapon-system separation

- 2014 pregens use 2014 weapon rules. They do not receive the 2024 Weapon Mastery system unless an explicit 2014 source rule independently grants equivalent behavior.
- 2024 pregens use 2024 weapon rules and any legally granted Weapon Mastery properties.
- Weapon Mastery is runtime behavior, not flavor text. Supported properties such as Cleave, Graze, Nick, Push, Sap, Slow, Topple, Vex, or other edition-defined mastery effects must resolve through universal primitives with exact 2024 timing/eligibility.
- Never add a class-name or character-name special case when a universal weapon/mastery primitive can express the rule.

## 5. Monster and pregen ingestion contract

Every new monster or pregen must follow the same rules-first pipeline:

1. Identify the source edition and immutable source definition.
2. Parse/bind source rules into edition-specific declarative data.
3. Map combat-relevant behavior to existing universal combat primitives.
4. If a required primitive truly does not exist, add one reusable universal primitive rather than name-specific code.
5. Preserve exact edition timing, targeting, action cost, resources, durations, saves, attacks, damage, conditions, movement, and restrictions.
6. Fail closed on unsupported outcome-changing mechanics.
7. Certify Python reference behavior and browser production behavior with permanent regression coverage.
8. Generate/export runtime artifacts from the certified source; never hand-edit generated monster or pregen registries.
9. Mark the card runnable only after ruleset-specific certification passes.

## 6. Blocker classification before coding

Before writing a new mechanic, classify a blocked monster/pregen feature as one of:

1. `ENGINE_EXISTS_BINDING_MISSING`
2. `ENGINE_EXISTS_CERTIFICATION_MISSING`
3. `ARENA_NEUTRAL`
4. `ENGINE_TRULY_MISSING`

Only `ENGINE_TRULY_MISSING` justifies a new universal engine mechanic. Arena-neutral classification is allowed only when the source rule cannot change an Iron Pit combat outcome.

## 7. Test-lane minimum

The immediate playable test target is:

- at least 100 certified 2014 monsters;
- at least 100 certified 2024 monsters;
- at least one canonical 2014 class/subclass legal and runnable at every level 1–10;
- at least one canonical 2024 class/subclass legal and runnable at every level 1–10;
- the ruleset selector must prevent cross-edition pairings;
- Step, Watch, Replay, and Turbo must consume the same canonical resolver/event stream;
- a runtime or rules error is never silently converted into a legal combat result.

## 8. Current implementation priority

Do not delay the first playable test lane to complete every monster, every class, or homebrew authoring. First prove accurate end-to-end fights under both editions. Homebrew 2014 and Homebrew 2024 remain separate future authoring surfaces and must eventually feed this same validated edition-specific pipeline.
