# Current operating status

Updated 2026-10-08 after arena PR #661 merge.
Current arena merge: `638fbd27f4dee38a3d93aab3101fde20e9651b99`. Monster source-classifier figures below are from the generated blocker report on `main`, not a new full runtime certification. See the fix tracker for exact-head workflow evidence.
Active fix queue: [Monster fix tracker](MONSTER_FIX_TRACKER.md).
Per-monster source blockers: [Generated 2014 list](MONSTER_BLOCKERS_2014.md).

This file is operating authority for **what to work on next**. Combat rules remain authoritative in `docs/IRON_PIT_RULES_CONTRACT.md`. Generated certification manifests and exact current source/tests determine counts and readiness. Repository truth overrides chat summaries and older milestone prose.

## Verified baseline and current queue

Arena PRs #658 (one-square footprints), #660 (3x2 deployment) and #661 (mixed combatant teams) are merged. Production Netlify remains locked. The last full monster certification baseline described here was PR #637; do not carry its counts forward as current runtime certification.

Current generated 2014 blocker source classification: **201/327 admitted, 126 blocked** (`docs/MONSTER_BLOCKERS_2014.md`). This is **not** a statement that all 201 have passed a new exact-head runtime certification. Previously verified canonical pregens: 240/240 each edition; earlier 2024 monster baseline: 141/330. Reverify those totals against current generated manifests before publishing a new certification claim.

M-022 Berserk merged #651; M-023 Fey Ancestry merged #652; M-024 Gnome Cunning merged #653. Active work: M-025 Steadfast, draft #662 (clean generic active-ally predicate); #654 remains conflicted and should not be merged. M-026 Infernal Wound follows. Require exact-head Python/browser parity and certification for M-025 before calling it complete.

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

Complete M-025 as conditional Frightened immunity when an active ally exists. Reuse the universal active-ally predicate and condition-immunity modifier rather than creating a Steadfast-specific resolver. Implement and certify Python/browser live ally-context parity, refresh generated inventory/blockers, then merge the clean PR only if all required exact-head checks pass. Keep unrelated M-026 Infernal Wound separate.

## Publishing

Netlify production publishing remains manual/locked. Do not spend Netlify credits for monster-development validation.

## Verification truth

Only claim:

- **implemented** when code exists on the stated SHA;
- **tested** when relevant permanent tests ran on that exact code;
- **CI green** when exact-head workflows completed successfully;
- **certified** when current generated manifests, runtime data, and certification gates agree.

Never carry counts or CI status across a commit change without re-verification.
