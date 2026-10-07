# Iron Pit context transfer

generated_at: 2026-10-07, after PR #635 merge
main_sha: `f351f8ca725b2fea8789bbb0a79757b7a99b57de` (accepted merged source; later closeout documentation adds no behavior)
active_lane: finish 2014 source monsters through universal primitive reuse

## Accepted status

#635 cleared Violet Fungus: optional bounded random whole-sequence repetitions use the shared dice service, log one feature roll after one Action spend, freeze slots and reuse normal attacks/retarget/interruption/reset. Preview uses mean printed potential without rolling. No target means no count roll/spend. Count is local to this Action and never stored on cards/fight state. #633 cleared Grick previous-hit/same-target follow-up; #632 cleared both Veterans; #631 cleared Bandit Captain, Gladiator and Lizardfolk.

## Active PRs

No remaining active combat PR at closeout. #635 feature head `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff` passed all four required gates before merge.

## Verified certification

2014 monsters 191/327 (136 blocked), native 2024 141/330, heroes 240/240 each. CI: 2800 Python tests and 222 browser commands. Focused local source/schema/parity: 70 Python cases, seven new browser scenarios plus affected prior fixtures. [Exact-head evidence](MONSTER_FIX_TRACKER.md). Documentation successors inherit no exact-head CI claim.

## Current subsystem

Shared AttackActionDefinition: slots or complete variants. Optional PreviousAttackRequirement on slots checks the preceding slot's actual hit/target. Optional AttackSequenceRepetition on variants carries strict dice, bounded to eight expanded slots. Shared choice/loop owns current range/target/line legality, costs, dice, reactions, termination and fresh reset. Source binders prove printed source only; no creature/ability-name dispatch. Browser serializer supports package/direct-script imports and optional predicates/repetition metadata. Source cards remain immutable; fight state is disposable.

## Open correctness/architecture debt

No unresolved defect in the accepted sequence families. M-015 Brass Sleep Breath is next: shared timed Unconscious/ends-on-damage facts exist, but source save binding and printed Action-to-wake exit must be audited together. Wyrmling/Young/Adult each have only the save-action blocker; Ancient also has an extra-action blocker. Medusa Petrifying Gaze and remaining generated mechanics remain fail-closed (136 cards).

## Locked decisions / parked work

Rules contract §10: legal melee reach, otherwise ranged; highest compatible printed mean damage; printed counts/order preserved; fixed shield/offhand facts. Universal architecture includes previous-slot predicates and random sequence repetition. AGENTS: one focused family pass then required final-head CI, no duplicate local full suites. Grok owns art/presentation; Netlify stays locked. No independent 2024 expansion before 2014 completion.

## Next exact action

M-015: audit the shared sleep/wake-on-damage/Action-to-wake lifecycle against Brass Dragon Sleep Breath, then bind exact source saves/cones/durations/recharge through reusable primitives.

## Do not carry forward

Old 190/327 counts as current, Grick/Veterans/Violet Fungus blocked claims, prior-head CI or collection-failure statuses, row-based selection, or unmerged #625 implementations. Repository truth supersedes cached handoffs.
