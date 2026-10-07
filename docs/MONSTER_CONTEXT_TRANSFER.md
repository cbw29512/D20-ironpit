# Iron Pit context transfer

generated_at: 2026-10-07, after PR #631 merge
main_sha: `7c1199a4a4d1c6241b472bc28eadb235d58b8910` (merged source baseline; subsequent closeout documentation changes no combat source)
active_lane: 2014 monster completion through existing universal primitives

## Authoritative status

PR #631 merged. Complete source Multiattack alternatives select legal melee reach,
otherwise ranged, then highest printed damage. Fixed Gladiator shield remains
AC16; conditional two-handed Spear is preserved and unavailable with that loadout.
Cards remain immutable; normal attack resolution and fresh fight state own costs,
interruption, effects, and reset. Production is browser-only. Netlify stays locked.

## Active PRs

No remaining active combat PR at closeout. #631 final feature head was
`7034cf80341cb842c04a1b90a028e33cdb5525ad`; all required gates succeeded before merge.

## Recent merges

#631: legal reach/highest damage policy and complete Multiattack source alternatives.
#630: seven included weapon damage traits and magical qualifiers.
#629: susceptibility Dispel/Stunned and terminal antimagic.

## Verified certification

Source baseline: `7c1199a4a4d1c6241b472bc28eadb235d58b8910`. 2014 monsters 187/327; 2024 monsters
141/330; heroes 240/240 in each edition. CI: 2,760 Python tests, all 219 browser
commands. Local final focused pass: 133 tests. [Exact-head gates](MONSTER_FIX_TRACKER.md).

## Current subsystem

Immutable `AttackActionDefinition` uses ordinary slots or complete variants.
`unavailable_reason` preserves conditional attacks incompatible with fixed gear.
Python: attack_action_sequences / attack_action_choices / attack_actions.
Browser: formation / multiattack-choices / multiattack. Generated path: capability
registry, browser serializer, static site/exporters, certification manifests.
Permanent tests: source sequence proof/mutations, source-derived JSON oracle parity,
range policy in both editions, atomic rejection, natural 1, immutable card/reset.

## Open A-class correctness debt

No unresolved defect in the certified sequence tranche. Unsupported source mechanics
remain fail-closed blockers: Medusa Petrifying Gaze; Veteran/Half-Red Dragon Veteran
conditional offhand binding; Grick hit follow-up; Violet Fungus random count.

## Open B-class architecture debt

Future source-only bindings should consume the certified sequence/availability
schema; do not recreate attack resolution or mutable equipment state.

## Parked C-class cleanup

Grok owns art/presentation. No art edits belong in this lane.

## Locked decisions

Rules contract §10: legal reach selects weapon mode, highest legal printed damage,
printed counts/combinations retained, Gladiator keeps shield. Universal architecture:
source-preserving slots/variants and fixed availability facts. AGENTS.md: one
focused changed-family verification and one final-head CI pass; no duplicate full
local validation.

## Next exact action

Bind Veteran/Half-Red Dragon Veteran compatible source offhand loadouts through
existing slots/variants and availability facts (M-012), preserving all conditional
printed attacks.

## Do not carry forward

Old 184/327 baseline, superseded row-choice assertions, old blocked-card claims,
prior-head CI results, or unmerged #625 implementations. Reconstruct repository
truth if main or a feature head changes.
