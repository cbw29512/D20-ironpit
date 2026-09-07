# Current execution focus

This file records the active development priority for D20 Iron Pit. It supplements `IRON_PIT_MASTER_PLAN.md`; generated manifests remain the authority for certification counts.

## Locked priority: inventory first, implement families second

The unit of engine work is a reusable combat mechanic family, not an individual monster, hero, class, subclass, or named feature.

1. Inventory every combat-relevant mechanic used by the full 330-monster source roster.
2. Inventory every combat-relevant mechanic required by the 12 canonical pregens across levels 1-20, including subclass overlays, spell packages, feature choices, and loadout capabilities.
3. Normalize repeated behavior into reusable engine capability families.
4. Rank families by immediate monster unlock yield, total monster reach, pregen reuse, and cross-roster reuse.
5. Implement the highest-value generic family with Python/browser parity and deterministic permanent regressions.
6. Re-run the manifests and batch-promote every monster and hero level that is now fully representable.
7. Repeat until the target monster roster and canonical pregen roster are covered.
8. Run deterministic battle matrices continuously as coverage grows and use failures to harden shared mechanics, AI policy, logs, and invariants.

Do not return to a routine one-monster-at-a-time queue when several blocked cards share the same missing mechanic. A monster-specific tranche is justified only when it proves or exercises a reusable capability family.

`scripts/report_capability_yield.py` remains the detailed monster blocker report. `scripts/report_universal_engine_backlog.py` is the cross-roster backlog view and must be consulted before choosing a new engine tranche. `data/roster_combat_mechanics_v1.json` is the derived pregen mechanic inventory; certification manifests remain the authority for what is actually public-ready.

## Universal and homebrew rule

Content declares mechanics; content does not own engine behavior.

- A monster, pregen, spell, item, or homebrew card must compose existing engine capabilities whenever its timing, targeting, resource, roll, damage, condition, movement, and lifecycle semantics already match them.
- Never add a creature-name, class-name, subclass-name, or feature-name branch to the combat engine when a generic capability can express the same behavior.
- If a homebrew ability is only a renamed or recombined form of existing mechanics, it requires content data only.
- If a homebrew ability has genuinely new outcome-changing semantics, the engine may gain a new reusable capability. That capability must be generic enough for any future content to declare.
- Unknown outcome-changing semantics fail closed until Python, browser, serialization, logging, and deterministic regression coverage agree.

This makes official content the initial engine vocabulary rather than a permanent ceiling. New homebrew can extend the vocabulary without creating parallel combat systems.

## Hero completion rule

Hero levels still derive incrementally: level N derives from level N-1 and adds only the audited level-N delta. However, implementation order is driven by reusable capability yield rather than blindly walking one hero to level 20.

When a newly implemented family unlocks multiple hero levels, certify all of those levels as a batch. Already-certified snapshots remain valid anchors and must not be rebuilt independently unless their shared capability changes.

## Engine perfection checklist

A mechanic is not production-ready until both Python and browser resolve it identically and deterministic regressions cover the real encounter path. Priority families include:

- attacks, critical hits, Advantage/Disadvantage, AC, Saving Throws, and typed damage defenses;
- Action, Bonus Action, Reaction, movement, Dash, Opportunity Attacks, Extra Attack, and forced movement;
- conditions, immunity, duration, expiry, removal, source ownership, and cross-condition interactions;
- 0 HP, Death Saves, healing, Temporary HP, max-HP changes, stabilization, instant death, regeneration, and death triggers;
- Concentration and interruption;
- spell attacks, save spells, healing spells, buffs/debuffs, areas, targeting, exact spell-slot/resource use, and periodic effects;
- recharge, limited-use resources, refresh rules, generic reaction triggers, and feature interactions;
- auras, Legendary Actions, Legendary Resistance, transformations, summons, and dynamic combatants where required by target content;
- deterministic competent AI that simplifies decisions without changing RAW resolution;
- complete audit-grade combat logs sufficient to reconstruct why an outcome occurred;
- fail-closed handling for unsupported outcome-changing mechanics.

## Battle-testing gate

Automated battle matrices should grow with the roster rather than wait for content completion.

Battle testing should include:

- hero-vs-monster and team-vs-team deterministic seeded runs;
- mirrored-side and repeated-seed checks to detect side/order bias;
- invariants preventing illegal actions, negative resources, impossible HP, stale conditions, duplicate turns, or post-death actions;
- replayable logs for every failure;
- Python/browser outcome parity on identical seeds and rosters;
- aggregate metrics for win rate, rounds, damage, healing, resource use, deaths, and action-selection frequency.

Balance results are diagnostics, not permission to change RAW mechanics. Fix illegal behavior, AI mistakes, or implementation errors first; do not tune legal class/monster statistics merely to equalize win rates.

## Git/CI rule

PR #34 remains open, draft, and unmerged. Every promotion must clear exact-head permanent CI after generated artifacts are synchronized. Bot-authored generated commits are not final checkpoints by themselves; follow them with a normal connector commit and certify that exact head.
