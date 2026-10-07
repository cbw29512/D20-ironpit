# Current operating status

Updated 2026-10-07 after PR #641 merge.
Merged source baseline audited: `50c4e528a9db4987f5e57c40c89602556a4f2217`. See the fix tracker for exact-head workflow evidence.
Active fix queue: [Monster fix tracker](MONSTER_FIX_TRACKER.md).
Per-monster source blockers: [Generated 2014 list](MONSTER_BLOCKERS_2014.md).

This file is operating authority for **what to work on next**. Combat rules remain authoritative in `docs/IRON_PIT_RULES_CONTRACT.md`. Generated certification manifests and exact current source/tests determine counts and readiness. Repository truth overrides chat summaries and older milestone prose.

## Clean baseline

PR #624 is the historical reset point. PR #641 is the latest accepted monster tranche. #640 cleared Bronze Dragon Repulsion Breath through shared failed-save forced movement; #641 cleared Gorgon Petrifying Breath through shared staged condition escalation. All four final-head gates passed on both tranches; 2014 is 197/327. #637 cleared Brass Sleep Breath; #635 cleared Violet Fungus; #633 cleared Grick; #632 cleared both Veterans; #631 cleared Bandit Captain, Gladiator and Lizardfolk.
The required gates for every new mechanic tranche are:

- CI;
- 2014 Basic Roster;
- Paired Edition Monster Report;
- 2014 Hero Certification.

PR #625 is **closed unmerged**. It remains reference material only. It demonstrated useful mechanics, but it crossed too many semantic families to be a trustworthy merge unit.

Do not revive or extend #625. Reimplement only still-correct pieces from current `main` in small semantic batches.

## Verified current certification

| Edition | Content | READY / target |
|---|---|---:|
| 2014 | Canonical pregens | **240 / 240** |
| 2024 | Canonical pregens | **240 / 240** |
| 2014 | Source monsters | **197 / 327** |
| 2024 | SRD monsters | **141 / 330** |

Counts above were verified on the #641 merged source baseline. The tracker records exact-head gates. Later documentation-only commits add no combat behavior and do not inherit exact-head CI.

## Current completion order

1. Finish the 2014 source monster roster first.
2. Classify blockers by semantic behavior, not printed trait name.
3. Choose the largest coherent blocker family that maps to **one** universal primitive family.
4. Reuse an existing primitive whenever semantics match.
5. Keep one semantic mechanic family per PR.
6. Regenerate all derived data from that exact branch head.
7. Require Python/browser parity and all four exact-head gates before merge.
8. After each merge, re-audit all 327 2014 monsters and update the blocker counts.
9. Immediately audit 2024 for direct reuse of the completed primitive.
10. Do not expand independent 2024 mechanics while 2014 remains incomplete.

Pregens are complete and are not the active expansion lane.

## Anti-drift rules

- No monster-name or ability-name resolvers.
- No second primitive for behavior already represented by the engine.
- No hand-edited generated monster bundles.
- No count-only fixes that hide a blocker.
- No mixing unrelated mechanic families in one PR.
- No carrying CI or certification claims across a changed head SHA.
- No stale branch rebases merely to preserve work.
- No lair actions; monsters are not in their lairs.
- No ethereal/incorporeal arena escape behavior.
- Source cards/templates remain immutable; fight-only buffs/debuffs live in combat state and reset with the fight.

If a branch exposes an unrelated blocker, record it for the next tranche rather than absorbing it unless it is strictly required for the current family to become runnable.

## Monster blocker classification

Before implementation classify each unresolved behavior as exactly one of:

- `ENGINE_EXISTS_BINDING_MISSING`
- `ENGINE_EXISTS_CERTIFICATION_MISSING`
- `ARENA_NEUTRAL`
- `ENGINE_TRULY_MISSING`

Only `ENGINE_TRULY_MISSING` justifies a new universal engine primitive.

## Immediate next action

Next: M-018 Cyclops Poor Depth Perception. Cyclops is a single-blocker `source:trait` card. Bind its printed distance threshold as source data to a generic distance-based attack-roll Disadvantage source. The engine must not dispatch on Cyclops or Rock. Exact source threshold remains content data.

#641 is complete: Gorgon is admitted through shared staged condition escalation. #640 cleared Bronze Dragon Wyrmling and Young Bronze Dragon; Adult and Ancient Bronze lost their Repulsion Breath blocker but remain parked on independent extra-action behavior. Generated current-main blockers show **197/327 admitted and 130 blocked**.

Verification follows the single-batch policy in AGENTS.md: one focused changed-family check and one required final-head CI pass. Do not duplicate full CI locally or restart clean validation while monsters await implementation.

Historical work from #625 may be used as evidence, but every reused behavior must be revalidated against current main and implemented in a fresh branch.

## Publishing

Netlify production publishing remains manual/locked. Do not spend Netlify credits for monster-development validation.

## Verification truth

Only claim:

- **implemented** when code exists on the stated SHA;
- **tested** when relevant permanent tests ran on that exact code;
- **CI green** when exact-head workflows completed successfully;
- **certified** when current generated manifests, runtime data, and certification gates agree.

Never carry counts or CI status across a commit change without re-verification.
