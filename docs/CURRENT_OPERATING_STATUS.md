# Current operating status

Recorded 2026-10-06 after the monster-work baseline reset.
Main baseline audited: `007453194fcd5621c0130ffcabf25d3b132a1a07`.

This file is operating authority for **what to work on next**. Combat rules remain authoritative in `docs/IRON_PIT_RULES_CONTRACT.md`. Generated certification manifests and exact current source/tests determine counts and readiness. Repository truth overrides chat summaries and older milestone prose.

## Clean baseline

The last accepted monster baseline is merged PR #624. Its exact head passed all four required gates before merge:

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
| 2014 | Source monsters | **177 / 327** |
| 2024 | SRD monsters | **141 / 330** |

Counts above are the clean-baseline counts. Recompute them after every merged monster tranche.

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

Run the full 2014 blocker audit from clean main `007453194...`, group the remaining blockers by semantic mechanic, and take the largest **single-family** batch first.

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
