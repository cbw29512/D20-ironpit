# Complete Multiattack sequence audit

Owner: ChatGPT. Branch: `fix/2014-multiattack-sequences`. Status: ACTIVE.
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
conditional drawn offhand, Grick hit-dependent follow-up, and Violet Fungus random
count are separate parked behaviors.

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

Local source audit compiled all 187 admitted 2014 cards. Generated manifests agree:
240 heroes per edition, 187/327 2014 monsters, 141/330 2024 monsters. These are
current branch results, not a claim that exact-head CI has passed. Local validation
passed 131 focused Python tests, all 219 CI browser commands, and the backend-free,
Pages entry, battlefield wiring, and Netlify configuration checks. Required four
exact-head workflow results and merge SHA will be recorded after completion.

Touched debt repaired: row/reach contract conflict; incomplete rider damage scoring;
attack counter mutation before legality; duplicated source paragraph parsing;
sequence schemas shared by compiler and runtime; legacy area-slot counts preserved;
catalog/roster sentinels regenerated for the actual three-card admission.
