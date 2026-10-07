# Iron Pit context transfer

generated_at: 2026-10-07, after PR #632 merge
main_sha: `d84b26ab5f3f3170cb1c4d86721bfbfd38546bea` (merged source baseline; subsequent closeout documentation adds no combat behavior)
active_lane: finish 2014 source monsters through universal primitive reuse

## Authoritative status

#632 cleared Veteran and Half-Red Dragon Veteran through source-only fixed offhand binding. Both begin with one-handed Longsword plus drawn Shortsword; complete melee sequence is two Longswords + one Shortsword (21.5 mean). Two-handed Longsword remains preserved/unavailable; Crossbow is one standalone ranged attack. AC 17/18 and Half-Red Dragon Veteran Fire Breath are unchanged. No runtime resolver changes. Source cards remain immutable; fight state resets normally. Netlify remains locked; Grok owns art/presentation.

## Active PRs

#632 completed; no other active combat PR at closeout. Feature head `b3cc251beec8b74e8711590f15a09128528ecc09` passed all four gates before merge.

## Recent merges

#632: both 2014 Veterans, generic offhand source proof and source-path gate correction.
#631: full Multiattack alternatives; cleared Bandit Captain, Gladiator, Lizardfolk.
#630: included damage traits/qualifiers. #629: Dispel Stunned/terminal antimagic.

## Verified certification

2014 monsters 189/327, native 2024 monsters 141/330; heroes 240/240 each edition.
CI passed 2774 Python tests and all 220 browser commands. Focused local source/parity evidence: 25 Python cases, four browser cases. [Exact-head gates](MONSTER_FIX_TRACKER.md). Documentation-only successors carry no exact-head CI claim.

## Current subsystem

Immutable AttackActionDefinition uses ordinary slots or complete variants. Fixed conditional attack availability is source data. New source-only helper `monster_offhand_loadout_2014.py` validates wording/counts/IDs and hand compatibility; shared paragraph/two-hand source proof lives in `monster_source_sections_2014.py`. Existing sequence selectors/resolvers own preview, costs, targets, interruption, reactions and fresh reset. Python/browser parity fixture: `veteran-multiattack.json`; freshness and permanent source mutation tests accompany it. Required generators and manifests are current.

## Open A-class correctness debt

No unresolved defect in the accepted Veterans family. Grick remains blocked by hit-dependent same-target Beak follow-up. Violet Fungus remains blocked by random 1d4 attack count. Medusa still lacks Petrifying Gaze. Other unsupported behavior remains fail-closed in generated blocker list (138 cards).

## Open B-class architecture debt

Classify reuse before adding conditional sequence/target/repetition support. Never create another attack resolver or source-name dispatch.

## Parked C-class cleanup

Grok art/presentation stays outside this lane. No repeated broad checking of unchanged engine code.

## Locked decisions

Rules contract §10: legal melee reach, otherwise ranged, highest compatible printed damage; printed counts/combinations preserved. Fixed offhand preparation for both Veterans; fixed shield for Gladiator. AGENTS: one focused family pass then one required final-head CI pass, no duplicate local full suites.

## Next exact action

M-013: audit the existing hook/sequence primitives for Grick's previous-hit requirement and same-target follow-up, then implement only the missing generic semantics. M-014 Violet Fungus random count is separate.

## Do not carry forward

Old 187/327 baseline as current, Veterans blocked claims, prior-head CI status, row-based attack choice, or unmerged #625 implementations. Repository truth supersedes cached handoffs.

## Active M-013 branch

`feat/2014-grick-followup` is based on exact merged documentation main `ec84f726f799f03db78beacfe433c85b353f270f`. Grick uses generic previous-hit/same-actual-target slot predicates, sharing ordinary attack selection/resolution. Focused 58 Python cases plus eight new browser scenarios and affected sequence fixtures passed. Generated branch roster is 190/327, pending exact-head CI; accepted baseline above remains 189/327. Next action: allow four final-head gates to finish and merge on success. Source details and native 2024 audit are in GRICK_SEQUENCE_AUDIT.md.
