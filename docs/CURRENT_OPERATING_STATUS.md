# Current operating status

Updated 2026-10-07 after PR #631 merge.
Merged source baseline audited: `7c1199a4a4d1c6241b472bc28eadb235d58b8910`. See the fix tracker for exact-head workflow evidence.
Active fix queue: [Monster fix tracker](MONSTER_FIX_TRACKER.md).
Per-monster source blockers: [Generated 2014 list](MONSTER_BLOCKERS_2014.md).

This file is operating authority for **what to work on next**. Combat rules remain authoritative in `docs/IRON_PIT_RULES_CONTRACT.md`. Generated certification manifests and exact current source/tests determine counts and readiness. Repository truth overrides chat summaries and older milestone prose.

## Clean baseline

PR #624 is the historical reset point. PR #631 is the latest accepted monster tranche. Complete Multiattack alternatives and legal reach/highest damage selection passed all four exact-head gates. Bandit Captain, Gladiator, and Lizardfolk bring the 2014 baseline to 187/327.
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
| 2014 | Source monsters | **187 / 327** |
| 2024 | SRD monsters | **141 / 330** |

Counts above were verified on the #631 merged source baseline. The tracker records exact-head gates; documentation-only closeout commits do not add combat behavior. Documentation commits that follow this source baseline do not add combat behavior; recheck current repository truth before the next mechanic tranche.

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

Active M-012: Veteran and Half-Red Dragon Veteran source bindings are complete on `feat/2014-veteran-multiattack`, based on `14f0762205a4267c3cc43291a2ed2fe6bd772f70`. One focused family pass is clean; generated branch roster is 189/327. Await the four final-head CI gates, then merge and record accepted counts. No runtime engine changes or duplicate local full suites.

PR #631 is complete. Its [sequence audit](MULTIATTACK_SEQUENCE_AUDIT.md) records the source combinations, fixed Gladiator shield, native 2024 differences, and all exact-head gates. [140 blocked 2014 cards](MONSTER_BLOCKERS_2014.md) retain their other mechanics. Medusa's sequence is bound but Petrifying Gaze remains unsupported.

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
