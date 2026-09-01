# Current execution focus

This file records the active development priority for D20 Iron Pit. It supplements `IRON_PIT_MASTER_PLAN.md`; generated manifests remain the authority for certification counts.

## Locked priority

1. Combat engine correctness and Python/browser parity.
2. Finish the 12 canonical pregen progressions.
3. Build and run deterministic battle-testing harnesses against the existing certified monster pool.
4. Use battle findings to harden shared engine mechanics, AI policy, logs, and invariants.
5. Resume broad monster expansion only after the hero roster and battle harness are mature.

The existing monster pool is sufficient for current engine and hero testing. Do not spend routine development tranches increasing monster count unless a monster is needed to exercise a missing shared mechanic.

## Hero completion order

Progress breadth-first by level so all classes become battle-testable as early as possible:

- certify every canonical class at level 1;
- then every class at level 2;
- then level 3 with canonical subclasses;
- then level 4;
- then level 5;
- continue level-by-level through 20.

Already-certified higher-level snapshots remain valid anchors; do not regress or rebuild them independently.

Every hero level still follows the canonical rule: level N derives from level N-1 and adds only the audited level-N delta.

## Engine perfection checklist

A mechanic is not production-ready until both Python and browser resolve it identically and deterministic regressions cover the real encounter path. Priority families:

- attacks, critical hits, advantage/disadvantage, AC and cover assumptions;
- saving throws and typed damage defenses;
- action, Bonus Action, Reaction, movement, Dash, opportunity attacks, and Extra Attack;
- conditions, immunity, duration, expiry, removal, and source ownership;
- 0 HP, Death Saves, healing, Temporary HP, max-HP changes, stabilization, and instant death;
- Concentration and interruption;
- spell attacks, save spells, healing spells, buffs/debuffs, areas, targeting, and exact spell-slot/resource use;
- class/subclass resources, limited uses, refresh rules, and feature interactions;
- deterministic competent AI that simplifies decisions without changing RAW resolution;
- complete audit-grade combat logs sufficient to reconstruct why an outcome occurred;
- fail-closed handling for unsupported outcome-changing mechanics.

## Battle-testing gate

As soon as all 12 canonical level-1 heroes are certified, begin automated battle matrices while level-2+ certification continues.

Battle testing should include:

- hero-vs-monster and team-vs-team deterministic seeded runs;
- mirrored-side and repeated-seed checks to detect side/order bias;
- invariants preventing illegal actions, negative resources, impossible HP, stale conditions, duplicate turns, or post-death actions;
- replayable logs for every failure;
- Python/browser outcome parity on identical seeds and rosters;
- aggregate metrics for win rate, rounds, damage, healing, resource use, deaths, and action-selection frequency.

Balance results are diagnostics, not permission to change RAW mechanics. Fix illegal behavior, AI mistakes, or implementation errors first; do not tune legal class/monster statistics merely to equalize win rates.

## Git/CI rule

PR #32 remains open, draft, and unmerged. Every promotion must clear exact-head permanent CI after generated artifacts are synchronized. Bot-authored generated commits are not final checkpoints by themselves; follow them with a normal connector commit and certify that exact head.
