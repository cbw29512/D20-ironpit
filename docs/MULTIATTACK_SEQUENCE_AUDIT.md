# Complete Multiattack sequence audit

Owner: ChatGPT. Branch: `fix/2014-multiattack-sequences`. Status: DONE, merged #631.
Starting main: `d9dc236477e85a86dcaacfd99470abdd883ad11f`; no overlapping open PR at intake.
Scope: immutable sequence schema, shared attack selection/legality, source bindings,
serializer, generated rosters, and permanent Python/browser tests. Grok's art files
remain outside this tranche.

## Source and reuse decision

Classification: `ENGINE_EXISTS_PARAMETER_DELTA`. Ordinary ordered attack/save slots,
Action spending, attacks, saves, damage, reactions, natural-1 termination, and reset
already exist. Extend their immutable input with complete alternatives; do not add
another attack resolver. Rules authority: rules contract §10. Chris selected legal
melee reach, otherwise ranged, then highest legal damage; Gladiator retains shield.

| 2014 source | Complete alternatives | Remaining blocker |
|---|---|---|
| Bandit Captain | Two Scimitar + one melee Dagger; or two ranged Daggers | None after binding |
| Gladiator | Three legal melee choices; or two ranged Spears | None after binding; two-handed Spear preserved but unavailable with shield |
| Lizardfolk | Two different melee weapons: all 12 ordered legal pairs | None after binding; ranged Javelin remains a standalone attack |
| Medusa | One Snake Hair + two Shortswords; or two Longbows | Petrifying Gaze (`source:trait`) |

Pinned source paragraphs prove counts, compulsory weapon combinations, and
mode. Mutated counts, missing wording, empty choices, and unknown attacks fail
closed. Source actions/cards remain intact. Veteran/Half-Red Dragon Veteran
conditional drawn offhand was subsequently completed in M-012 below. Grick
hit-dependent follow-up and Violet Fungus random count remain queued.

## Schema, lifecycle, and parity map

| Surface | Binding / resolution |
|---|---|
| Shared immutable schema | `domain/attack_action_definitions.py`: either ordinary slots or complete variants; all branches validated |
| Source proof | `monster_multiattack_variants_2014.py`; shared `monster_source_sections_2014.py` parser |
| Python choice | `attack_action_sequences.select_sequence` -> existing `attack_action_choices.attack_choice` |
| Python execution | Existing `attack_actions.resolve_attack_action` slot loop; direct attack legality rejects unavailable equipment before attack counting |
| Browser choice | `browser-multiattack-choices.selectSequence` -> existing `formation.chooseSlotAttack` |
| Browser execution | Existing `browser-multiattack.resolveAttackAction` loop; `browser-attack` rejects unavailable equipment |
| Serialization | `browser_template_serializer.py`; variants and conditional attack availability preserved |
| Lifecycle | Selection is local to one Action and frozen before spending. No new mutable resource, equipment state, or timer. Ordinary fresh fight state resets costs/HP/effects |
| Permanent evidence | Source mutation and schema tests, range-policy tests in both editions, source-derived checked-in fixture with Python freshness check and production website browser loader |

Preview and resolution select the same complete sequence. Target choices still
use ordinary target legality; the sequence never gains a strike by mixing branches.
Highest printed mean damage includes base/fixed damage and printed on-hit riders.
Unsupported/malformed branches are validated even when they would not be selected.
Multiattack remains distinct from the player Attack action and grants no Light/Nick.

## Immediate native 2024 audit

All 330 native records and the paired runtime report were inspected. Source numbers
were not copied across editions. Paired report: 187/327 admitted in 2014; 141/330
in 2024; 288 shared identities, 114 both READY, six 2014 catch-up candidates.

| Native 2024 source | Independent result |
|---|---|
| Bandit Captain | Two attacks using Scimitar/Pistol in any combination; existing ordinary slots suffice. It does not get the 2014 three/two counts or Daggers |
| Gladiator | Three Spear attacks, with one Shield Bash save replacement. Still independently blocked; it does not get the 2014 two-ranged limit or on-hit Shield Bash |
| Medusa | Two Claws + one Snake Hair, or three Poison Rays. Different count/composition; no 2014 Shortsword/Longbow data copied |
| Lizardfolk | No same-name native SRD counterpart; no synthetic 2024 card created |

Both editions automatically reuse the updated generic range/damage selection.
Independent 2024 binding expansion remains outside the 2014 completion lane.

## Verification truth

Verified feature head: `7034cf80341cb842c04a1b90a028e33cdb5525ad`. Merged source baseline: `7c1199a4a4d1c6241b472bc28eadb235d58b8910`.
All 187 admitted 2014 source cards compiled. Generated manifests verify 240 heroes
per edition, 187/327 2014 monsters, and 141/330 2024 monsters. CI passed 2,760
Python tests and all 219 browser commands. Local focused verification passed 133
tests; production wiring/build checks passed. All four final-head gates succeeded:

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999836): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999753): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999736): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999745): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.

These gates certify the feature head. Later documentation-only commits do not
inherit its CI result. Netlify production remains locked.

Touched debt repaired: row/reach contract conflict; incomplete rider damage scoring;
attack counter mutation before legality; duplicated source paragraph parsing;
sequence schemas shared by compiler and runtime; legacy area-slot counts preserved;
catalog/roster sentinels regenerated for the actual three-card admission.

## M012 — Veteran source binding (2026-10-07)

Base `14f0762205a4267c3cc43291a2ed2fe6bd772f70`; branch `feat/2014-veteran-multiattack`. Reuses the merged complete-sequence engine without runtime changes. Both 2014 Veterans start with printed Shortsword drawn and Longsword in one hand. The complete 2 Longsword + 1 Shortsword sequence averages 21.5 damage versus 17 for two two-handed Longsword attacks. The conditional two-handed profile remains present but unavailable. At range, Heavy Crossbow is one standard attack, never a three-shot Multiattack. AC remains 17/18; Half-Red Dragon Veteran keeps its existing DC 15, 7d6 Fire Breath, 15-foot cone, Recharge 5–6.

Source proof checks wording, count, weapon names/kinds, every ID, and the exact conditional two-hand profile before admitting the whole card. Four source/compiler/browser parity cases cover both cards at 5/20 feet; malformed source variants fail closed. Roster becomes 189/327. One focused verification and one final-head CI pass; no duplicate local full suites.

Native 2024 audit: Warrior Veteran has two Greatsword or Heavy Crossbow attacks, with Greatsword 2d6+3 and Crossbow 2d10+1. Half-Dragon has two Claws with Draconic Origin damage and a distinct DC 14, 8d6, 30-foot Dragon’s Breath. These are different source cards; no 2014 offhand sequence or breath values are copied. 2024 readiness stays 141/330. Completed and merged [#632](https://github.com/cbw29512/D20-ironpit/pull/632). Final feature head `b3cc251beec8b74e8711590f15a09128528ecc09`; merged source `d84b26ab5f3f3170cb1c4d86721bfbfd38546bea`. CI passed 2774 Python tests and 220 browser commands; all required final-head gates passed:

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37569499249): success on `b3cc251beec8b74e8711590f15a09128528ecc09`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37569499169): success on `b3cc251beec8b74e8711590f15a09128528ecc09`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37569499130): success on `b3cc251beec8b74e8711590f15a09128528ecc09`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37569499153): success on `b3cc251beec8b74e8711590f15a09128528ecc09`.

Roster gate wiring: the historical path filter omitted source Multiattack binders and initially skipped M-012. Added the generic 2014 monster-source module pattern for both PR and push triggers so source-only families automatically receive the required roster gate. No combat code changed for this correction.
