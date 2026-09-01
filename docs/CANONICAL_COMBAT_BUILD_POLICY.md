# Canonical Combat Build Policy

This file is the authoritative mass-production policy for Iron Pit canonical heroes. It applies to every core class, every level 1-20 progression, generated browser data, certification, and any future canonical pregen pipeline.

## Core rule

Iron Pit builds one persistent canonical combat character per class and advances that same character from level 1 through level 20. A level is a deterministic RAW combat delta, not a separately hand-built character.

The intended pipeline is:

`canonical class identity -> deterministic legal level-1 combat build -> level delta -> reusable combat capabilities -> generated runtime/browser data -> generated certification`

Do not duplicate complete hero definitions per level when the same result can be derived from the previous level plus the current level's RAW changes.

## Legal deterministic base ability array

Use the 27-point-buy array below before Background increases or later feat/ASI increases:

`15 / 14 / 13 / 10 / 10 / 10`

This is the only default canonical base array for mass-produced Iron Pit heroes.

### Melee and weapon-first hybrids

The three mental abilities are 10. Assign 15/14/13 to the physical abilities in combat priority order.

- Strength-primary melee: STR 15, CON 14, DEX 13; INT/WIS/CHA 10.
- Dexterity-primary melee: DEX 15, CON 14, STR 13; INT/WIS/CHA 10.
- Dexterity-primary ranged: DEX 15, CON 14, STR 13; INT/WIS/CHA 10.

Canonical class defaults:

- Barbarian: STR 15, CON 14, DEX 13.
- Fighter: STR 15, CON 14, DEX 13.
- Monk: DEX 15, CON 14, STR 13.
- Paladin: STR 15, CON 14, DEX 13.
- Ranger: DEX 15, CON 14, STR 13.
- Rogue: DEX 15, CON 14, STR 13.

### Primary casters

STR, DEX, and CON are all 10. Assign 15/14/13 to the three mental abilities in deterministic class priority order.

- Bard: CHA 15, WIS 14, INT 13.
- Cleric: WIS 15, CHA 14, INT 13.
- Druid: WIS 15, CHA 14, INT 13.
- Sorcerer: CHA 15, WIS 14, INT 13.
- Warlock: CHA 15, WIS 14, INT 13.
- Wizard: INT 15, WIS 14, CHA 13.

This deliberate combat-simulation convention keeps three baseline non-priority saves at +0 before proficiency or later RAW modifiers while preserving a legal 27-point-buy character.

## Background and origin increases

Use only legal 2024 Background ability increases. Species does not receive invented ability-score bonuses.

- Prefer +2 to the canonical primary ability and +1 to the highest-ranked other allowed canonical ability.
- Keep a base 10 dump ability at 10 when a legal higher-priority allowed ability can receive the increase instead.
- If the selected Background cannot legally improve the canonical primary ability, choose another legal canonical Background or fail closed for human review; do not silently invent an increase.
- Record Background/origin choices in build metadata even when their noncombat effects are omitted from runtime combat data.

## Level 1-20 progression

Every level derives from the previous canonical level.

At each level update only the RAW combat delta plus derived values affected by that delta, including as applicable:

- proficiency bonus;
- hit points;
- ability scores from feats/ASIs;
- AC and Speed;
- attack/save bonuses and save DCs;
- attacks, damage, range/reach, Extra Attack/Multiattack;
- class/subclass/species combat features;
- resources and recharge/use counts;
- weapon masteries that actually affect the arena loadout;
- spell attack/DC, spell package, slots, concentration, healing, buffs/debuffs, reactions and Bonus Actions;
- defenses, conditions, resistances, immunities and movement effects.

Do not rebuild unchanged level data by hand.

## Combat-only runtime scope

Iron Pit runtime includes only data and abilities that can change an Iron Pit combat outcome.

Noncombat skills, languages, tools, exploration ribbons, social features, crafting, downtime features, and utility-only choices may remain in legal-build/source metadata but are omitted from the runtime capability surface and do not block combat certification.

If RAW requires a noncombat choice that cannot affect the arena, choose a legal class-relevant option deterministically or randomize among equivalent legal options. Do not spend custom engine work on it.

## Feat, ASI, spell, equipment, and subclass policy

- Select legal combat-facing options deterministically for the canonical build.
- Optimize for the character's established combat role without changing that role between levels.
- Prefer reusable policies over hero- or level-specific branches.
- A feat or ASI must update all derived combat values automatically.
- A caster extends one deterministic class spell package as levels unlock more prepared/known spells and slots; do not create a new spellbook for each level.
- Equipment changes only when a legal progression choice materially improves or is required by the canonical combat build.
- Once a canonical subclass is selected, progression remains on that subclass through level 20 unless the user explicitly changes the project architecture.

## Universal Combat Capability rule

Hero and monster combat behavior must reuse the same shared engine capability whenever RAW behavior is equivalent.

A hero/monster record should primarily describe stats, attacks, resources, spells, defenses, and capability IDs. New custom resolver code is justified only when the source introduces a genuinely new outcome-changing RAW mechanic.

If the capability already exists, adding a new hero level or monster should be data work plus generated certification, not a bespoke engine implementation.

## Fail-closed RAW rule

Never guess an outcome-changing combat mechanic.

- If RAW wording/timing/targeting/resource behavior is clear, implement it once in the shared engine and reuse it.
- If a combat-relevant rule is genuinely ambiguous or the automatic tactical choice materially needs user policy, stop that feature and ask the user rather than inventing behavior.
- Unsupported outcome-changing mechanics remain explicit blockers.
- Noncombat choices do not require this stop condition because they do not affect Iron Pit outcomes.

## Generated certification rule

One authoritative canonical definition must drive runtime templates, browser hero data, public catalog state, and certification manifests wherever practical.

Do not maintain repeated hand-authored ready lists or duplicate level facts when they can be generated from canonical source data. Existing duplicated bookkeeping is migration debt and should be removed or replaced by equally strong generated assertions during the architecture cleanup.

A level is certified only when its actual RAW combat capabilities are supported and the permanent Python/browser/generated/exact-head gates pass. Certification must never be created by manually editing generated manifests.

## Migration rule

Existing certified heroes that predate this policy must be migrated to this canonical array/data-driven architecture before their progression is extended further. Preserve already-correct reusable combat mechanics; change duplicated build bookkeeping rather than rewriting working engine behavior.
