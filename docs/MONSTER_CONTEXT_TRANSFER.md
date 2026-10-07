# Iron Pit context transfer

generated_at: 2026-10-07, after PR #633 merge
main_sha: `72d4a8d3e1aec7d9e70bc9154ec6f03e3cfc0e64` (accepted merged source; subsequent closeout documentation adds no behavior)
active_lane: finish 2014 source monsters through universal primitive reuse

## Accepted status

#633 cleared Grick with optional previous-slot hit/same-actual-target requirements. Source-proof binding requires one Tentacles, then Beak only after a hit against that same target. Normal current legality is rechecked after damage/reactions; dead/moved targets cannot be substituted. Redirected attacks use the actual recorded target. No new fight state/second attack resolver. #632 cleared both Veterans; #631 cleared Bandit Captain, Gladiator, Lizardfolk.

## Verified certification

Feature head `d3c8021d125e2a9f4aa001db89d2cca9758fca6f` passed all four gates before merge. 2014 monsters 190/327 (137 blocked), native 2024 monsters 141/330, heroes 240/240 each. CI passed 2,788 Python tests and 221 browser commands. Focused local evidence: 58 Python cases/eight new browser parity scenarios. [Exact-head gates](MONSTER_FIX_TRACKER.md). Later documentation-only commits carry no exact-head CI claim.

## Active work

#633 completed; no open combat PR at this closeout. M-014 branch `feat/2014-violet-fungus-repeat` has built optional random sequence repetition through the shared dice service/ordinary attack loop. Focused 70 Python cases, seven new browser cases and affected prior sequence fixtures passed. Re-anchor to merged documentation main and finish generation before its PR. Native 2024 Violet Fungus has fixed two attacks; no random parameter is copied.

## Current subsystem

Shared AttackActionSlot optionally declares PreviousAttackRequirement; complete variants retain printed order/count/kind. Source-specific binders only prove printed inputs. Attack choice accepts an optional target ID and reuses full normal legality. Preview assumes a preceding legal attack hits for printed potential scoring; execution checks its actual event. Serializer helper supports package and direct-script imports. Source/cards immutable, fight state disposable; fresh reset normal.

## Open correctness/architecture debt

Violet Fungus random-count tranche M-014 is active but not accepted yet. Medusa Petrifying Gaze and other mechanics stay fail-closed in the generated 137-card blocker list. Avoid source-name dispatch/new resolvers; classify missing semantics before adding primitives. No outstanding defect in the certified Grick family.

## Locked decisions and parked work

Rules contract §10 governs legal reach/highest compatible printed damage and fixed Gladiator shield/Veteran offhand. AGENTS requires one focused family pass then one final-head CI pass, no duplicate local full suites. Grok owns art/presentation. Netlify remains locked.

## Next exact action

Re-anchor completed M-014 source/schema/parity work to merged #633 closeout main, finish generation, push its final head and merge after all four required gates pass.

## Do not carry forward

Older 189/327 count as current, Grick blocked claims, initial #633 collection-failure head, prior-head CI statuses, row-based selection, or unmerged #625 code. Repository truth supersedes cached handoffs.

## M-014 final branch

`feat/2014-violet-fungus-repeat` is re-anchored to exact merged documentation main `8a5d37360aaf49f65198f4b145fe32a5af42e251`. Generated branch roster is 191/327, 136 blocked; focused 70 Python cases/seven new browser scenarios and affected prior fixtures passed. Exact final-head CI pending. Next action: let required four gates complete and merge on success. FUNGUS_SEQUENCE_AUDIT.md records source, lifecycle, roll evidence and native 2024 differences.
