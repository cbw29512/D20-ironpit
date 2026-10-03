# 2024 Paladin 12: cumulative Charisma advancement

Baseline: `ad53f23f7eaad83964aae694d0c27c10172813b8` (certified Paladin 11).

## Objective and source

Advance persistent Human Devotion Paladin Aurelia Brightshield by one legal
Ability Score Improvement, following the Strength → Charisma → Constitution
policy. Strength is already 20, so Charisma rises 15→17.

Official source checked: D&D Beyond Basic Rules 2024, Character Classes,
Paladin Features table and level-4 ASI (also granted at levels 8/12/16):
https://www.dndbeyond.com/sources/dnd/br-2024/character-classes#Paladin

## Schema and state first

- Immutable input: existing `AbilityIncrease(ability="charisma", amount=2)`
  appended at level 12; existing `AbilityScores` compiles all cumulative deltas.
- Mutable state: ordinary fresh `CombatantState`; no new state field.
- Timing/resource: ASI is build-time data, not a combat activation or cost.
- Lifecycle: source templates remain immutable; normal match construction
  restores HP/resources and discards conditions/modifiers between matches.

## Logic flow and semantic reuse

Base abilities → legal Soldier increases → levels 4/8/12 deltas → derived
Charisma modifier → existing aura, weapon buff, healing, save and skill data.

Classification: `ENGINE_EXISTS_PARAMETER_DELTA`. Shared ability-score math
already serves 2014 Paladin ASIs, 2024 Monk/Druid ASIs and monster stat data.
No class-specific combat resolver or new universal primitive is introduced.

## Parity map

- Python: profile/runtime builders; `friendly_save_auras.sync_friendly_save_auras`.
- Browser: generator-owned hero registry; shared browser friendly-save aura engine.
- Values: HP 100; Lay On Hands 60; Aura/Sacred Weapon +3; Abjure Foes DC 15,
  three targets; Charisma save/skills +7; Cure Wounds healing modifier +3.
- Slots stay 4/3/3; ordinary preparations stay ten per the 2024 class table.
- Regression: level-12 build audit, live aura range/shutdown, fresh-match state,
  level-11 stability and generated production-browser parity.

## Continuous debt pass

Split later feature audits so touched production files stay at or below 150
lines. Correct the old Channel Divinity source note to show three uses from
level 11. Preserve independent combat fingerprints and generated artifacts.
Netlify publishing lock is unchanged. Exact-head CI remains the merge gate.
