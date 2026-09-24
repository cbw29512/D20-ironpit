# 2014 Pregen Batch Preparation Plan

This file is a planning/work-sequencing aid only. It is **not** a readiness manifest and cannot make a hero READY.

## Objective

Finish the remaining canonical 2014 pregen work with less repeated full-suite overhead while preserving the existing RAW and universal-engine certification rules.

The batch starts from the current persistent 2014 Life Cleric completion. Work remains 2014-only until all twelve canonical 2014 classes reach level 20 and the full 2014 audit is complete.

## Development cadence

1. Prepare the remaining class lanes before opening a batch PR.
2. Preserve one persistent character per class from level 1 through level 20.
3. Before implementing a named feature, search existing hero and monster mechanics for equivalent behavior.
4. Bind equivalent behavior to existing universal primitives; use source-specific names only for cards/logs.
5. During implementation, run only targeted tests for the class/mechanics being changed.
6. Do not add a prepared class to the certified READY roster until its lane is actually complete.
7. When the prepared batch has been worked through, regenerate artifacts and run full 2014 Hero Certification plus repository-wide CI once as the batch merge gate.

## Carryover lane

### Devotion Paladin — Aurelia Brightshield
- Current certified boundary: level 12.
- First task: continue the **same Aurelia** from level 13 through level 20.
- Preserve species, background, subclass, equipment, prior ASIs, spell choices where legally persistent, and previously earned features.
- Audit every new level against existing universal mechanics before adding engine behavior.

## Six prepared class lanes

### Lore Bard — Lyra Silverstring
- Target: levels 1–20, one persistent 2014 character.
- Subclass: College of Lore.
- Preparation focus: legal ability/equipment progression, Bardic Inspiration resource/lifecycle, spellcasting progression, subclass combat features, and reuse of existing buff/debuff/save/healing/reaction primitives.
- No certification registration until the lane is complete.

### Land Druid — Thalen Greenbough
- Target: levels 1–20, one persistent 2014 character.
- Subclass: Circle of the Land.
- Preparation focus: spell preparation/slots, concentration, healing/control/damage primitives, and a specific audit of Wild Shape/form-state behavior against existing transformation/state primitives before any new resolver is considered.
- No certification registration until the lane is complete.

### Hunter Ranger — Rowan Ashtrail
- Target: levels 1–20, one persistent 2014 character.
- Subclass: Hunter.
- Preparation focus: martial attack progression, Fighting Style, ranger spellcasting, concentration/mark-style damage, Hunter feature choices, movement/targeting, and existing multi-target/attack-action primitives.
- No certification registration until the lane is complete.

### Draconic Sorcerer — Nyra Emberveil
- Target: levels 1–20, one persistent 2014 character.
- Subclass: Draconic Bloodline.
- Preparation focus: spells known/slots, Sorcery Points, Metamagic parameter changes, defensive passives, typed damage modifiers/resistances, and horizontal-use flight under the Iron Pit movement contract.
- No certification registration until the lane is complete.

### Fiend Warlock — Varek Ashenmark
- Target: levels 1–20, one persistent 2014 character.
- Subclass: Fiend Patron.
- Preparation focus: Pact Magic slot lifecycle, invocations, concentration/bonus damage, kill-triggered Temporary HP, save/check modifiers, source-owned resistance, Mystic Arcanum, and any temporary-removal/return effect as compositions of existing primitives where possible.
- No certification registration until the lane is complete.

### Evoker Wizard — Elian Starweaver
- Target: levels 1–20, one persistent 2014 character.
- Subclass: School of Evocation.
- Preparation focus: spellbook/preparation legality, slots/Arcane Recovery, area spells, save damage, auto-hit damage, friendly-area exclusions, damage modifiers, and limited-use/maximized-damage behavior through existing universal spell/damage primitives.
- No certification registration until the lane is complete.

## Per-class preparation packet

Before implementation begins for a class, its packet must contain:

- canonical identity and 2014 subclass;
- legal level 1 starting build;
- persistent ASI/feat/equipment decisions through level 20;
- class/subclass feature list by acquisition level;
- spell/resource progression where applicable;
- combat-relevant feature decomposition;
- existing universal primitive candidates found in hero and monster code;
- blocker classification for every uncovered behavior:
  - `ENGINE_EXISTS_BINDING_MISSING`
  - `ENGINE_EXISTS_CERTIFICATION_MISSING`
  - `ARENA_NEUTRAL`
  - `ENGINE_TRULY_MISSING`
- targeted tests required while implementing the lane.

## Batch completion gate

The batch is ready for a pull request only when:

- Aurelia reaches 20;
- Lyra, Thalen, Rowan, Nyra, Varek, and Elian each have a complete persistent 2014 level 1–20 implementation;
- no known combat-relevant feature is silently omitted;
- every true missing mechanic has Python/browser parity;
- targeted lane tests pass;
- generated artifacts are regenerated from canonical source.

Only then run the expensive full 2014 certification and repository-wide CI for merge.
