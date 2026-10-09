# Monster fix tracker

Updated 2026-10-07. Owner: ChatGPT for combat mechanics; Grok retains art/presentation ownership.

**Historical merge/evidence tracker. The current, reconciled monster-name → issue → remediation → planning/code status queue is [MONSTER_ABILITY_WORK_QUEUE.md](MONSTER_ABILITY_WORK_QUEUE.md). Read it first; this older tracker must not override its current cursor or cause an already answered user decision to be reopened.**

[Every blocked 2014 monster](MONSTER_BLOCKERS_2014.md)
is generated from current source; [current operating status](CURRENT_OPERATING_STATUS.md)
sets the work lane. Rules live in the rules contract, not this tracker.

## Active and deferred fixes

| Priority / ID | Status | Problem and scope | Next action / completion evidence |
|---|---|---|---|
| P0 M-001 | Complete, merged #629 | Complete 2014 Antimagic Susceptibility for Animated Armor, Flying Sword, and Rug of Smothering. Dispel uses existing Stunned for 10 rounds; antimagic uses shared terminal death. | Shared lifecycle tests, generators, and all four exact-head gates passed. [Detailed audit](ANTIMAGIC_SUSCEPTIBILITY_AUDIT.md). |
| P0 M-002 | Complete, merged #629 | Stale capability export and browser bundle caused resumed-head CI failure. | Regenerate from the branch; run export freshness checks and browser sentinel tests. Final-head export, static parity, and certification checks passed. |
| P0 M-003 | Complete, merged #629 | Terminal resolver extraction left three browser test loaders missing their production dependency. | Shared runtime loaded; all 217 CI browser commands passed. |
| P0 M-004 | Complete, merged #629 | Touched Stunned primitive omitted 2014 movement restriction. | Edition-aware shared speed predicates and permanent regressions passed in both runtimes. |
| P1 M-005 | Deferred | Rug of Smothering remains blocked by attack representation, extra action, and Damage Transfer. | Audit each behavior and classify reuse before implementation. Susceptibility alone does not certify the rug. |
| P1 M-006 | Next: M-022 | Remaining 2014 source roster is incomplete. | Continue source bindings through certified primitives; generated counts are authoritative after each merged tranche. |
| P1 M-007 | Audited for #629/#630 | Check 2024 source reuse without inventing matching traits. | Native 2024 constructs have no susceptibility; all 330 native trait texts lack the included weapon traits. No 2014 trait/qualifier copied. Repeat per family. |
| P1 D-001 | Complete | Operating status still referenced PR #624 and 177/327 despite newer main. | Current merged baseline and final-head verification recorded below and in operating status. |
| P1 M-008 | Complete, merged #630 | Seven 2014 source traits already include their damage: Brute (Bugbear/Gladiator), Heated Weapons (Azer/Salamander), Angelic Weapons (Deva/Planetar/Solar). | Pinned source validation, shared typed damage/magical qualifier, critical/defense/reset parity, and all four exact-head gates passed. Seven traits resolved; other card blockers remain. [Audit](INCLUDED_WEAPON_DAMAGE_AUDIT.md). |
| P1 M-009 | Deferred, separate contact tranche | Heated Body triggers on touching or a melee hit within 5 feet; current retaliation handles only melee hits. | Reuse retaliation damage and add a shared contact trigger only after schema audit. Azer/Salamander/Remorhaz remain blocked. |
| P1 M-010 | Deferred, separate grapple tranche | Salamander Tail automatically hits its own grappled target and cannot attack others; current policy lacks automatic hit. | Preserve source `auto_hit_own_grapple`; do not replace automatic hit with Advantage. |
| P1 M-011 | Complete, merged #631 | Printed alternative-count Multiattack previously blocked Gladiator (three melee or two ranged attacks) and the related Bandit Captain family. | Complete source alternatives bind Bandit Captain, Gladiator, Lizardfolk, and Medusa. First three are READY; Medusa retains Petrifying Gaze. Highest legal damage/reach policy, fixed shield, parity and all gates passed. [Audit](MULTIATTACK_SEQUENCE_AUDIT.md). |

| P1 M-012 | Complete, merged #632 | Veteran and Half-Red Dragon Veteran: two Longsword attacks plus conditional drawn Shortsword; two-handed Longsword is incompatible with held offhand. | Source-only binding, 25 focused Python cases, four browser parity cases, and all four exact-head gates passed. Ranged Crossbow stays one standard attack; AC/breath preserved. [PR #632](https://github.com/cbw29512/D20-ironpit/pull/632); [audit](MULTIATTACK_SEQUENCE_AUDIT.md). |
| P1 D-002 | Complete, Chris decision | Repeated broad verification displaced monster construction. | AGENTS.md records one focused changed-family pass and one final-head CI pass; no duplicate full local suites. |

| P1 M-013 | Complete, merged #633 | Tentacles hit permits one Beak attack against the same target. The printed dependency is now represented by immutable slot facts. | Generic previous-hit/actual-target requirements bind Grick. 58 focused Python cases, eight browser scenarios, and all four final-head gates passed. [Audit](GRICK_SEQUENCE_AUDIT.md). |
| P1 M-014 | Complete, merged #635 | Violet Fungus rolls 1d4 Rotting Touch attacks. | One logged count roll and one Action, ordinary attacks/retarget/interruption/reset. 70 focused Python cases, seven new browser scenarios, affected prior fixtures and all four final-head gates passed. [Audit](FUNGUS_SEQUENCE_AUDIT.md). |

| P1 M-015 | Complete, merged #637 | Brass Dragon Sleep Breath for Wyrmling/Young/Adult required failed-save Unconscious with damage expiry and a printed ally Action to wake; Ancient Brass also had an unrelated extra-action blocker. | Reused save-area, shared breath recharge, timed Unconscious, ends-on-damage, and generic `wake-sleeper`; source parameters remain edition/card data. All four exact-head gates passed. |
| P1 M-016 | Complete, merged #640 | Bronze Dragon Repulsion Breath reused shared save-area + forced movement; Wyrmling/Young became READY while Adult/Ancient retain unrelated extra actions. | Exact source push distances flow as source parameters; all four exact-head gates passed. |
| P1 M-017 | Complete, merged #641 | Gorgon Petrifying Breath reused staged Restrained -> repeat save -> Petrified lifecycle. | Generic failed-save escalation data now carries through the shared save pipeline; all four exact-head gates passed. |
| P1 M-018 | Complete, merged #643 | Cyclops Poor Depth Perception is Disadvantage beyond 30 ft.; Rock is 30/120, so universal long-range Disadvantage already represents the complete combat effect. | Source threshold/ranges were proved; no duplicate modifier primitive. All four exact-head gates passed. 2014 source classifier moved to 198/327. |
| P1 M-019 | Complete, merged #644 | Hobgoblin Martial Advantage reuses target-adjacent active-ally detection plus the generic once-per-turn +2d6 weapon-hit rider. | Shared adjacency and generic hit-rider mechanics; printed source name retained. |
| P1 M-020 | Complete, merged #645 | Yeti Fear of Fire binds applied fire damage to timed Disadvantage on attack rolls and ability checks until the end of its next turn. | Reuses shared typed-damage trigger and timed roll-scope modifier; exact-head fix merged. |
| P1 M-021 | Complete, merged #649 | Flesh Golem Aversion of Fire has the same printed combat semantics as Fear of Fire. | Reuses the universal fire-triggered timed Disadvantage rule under the printed name Aversion of Fire; exact-head gates passed. |\n| P1 M-022 | Active, clean replacement for closed #650 | 2014 Flesh/Clay Golem Berserk is represented as an ordinary persistent self-buff: printed HP threshold + d6 gate, nearest visible living creature regardless side, full-HP exit. | Reuses existing self-buff state, visibility, target order, movement, and attack legality. No fake Rage bonuses and no separate Berserk subsystem. Object fallback/creator calming follow the explicit Pit abstraction in rules contract §20.2. |

## Current evidence

Merged source baseline `403ec045b27391c50a4ca1cfb3cd2cac632e1291` from [PR #637](https://github.com/cbw29512/D20-ironpit/pull/637).
Verified feature head `af78af31111fd2c1f99396fc2d4639c13dbdebf4`: all four required exact-head gates passed.
2014 monsters **194/327 admitted**, **133 blocked**; native 2024 **141/330**; heroes **240/240** each edition.
CI passed **2800 Python tests** and **222 browser commands**. Local focused evidence: 70 Python cases, seven new browser scenarios and affected existing sequence fixtures. All required generated source/runtime/browser outputs agree. No duplicate full local suites.

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593683): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593740): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593727): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593731): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.

These gates verify the feature head; later documentation-only successors do not inherit exact-head CI. Historical tranche evidence is retained in the corresponding audits.

## Decision record

- 2026-10-06: Chris chose Dispel to kill susceptible constructs, then superseded
  that result with the shared Stunned debuff for one minute (10 rounds).
- The previous no-save selection is retained. HP remains unchanged. Stunned
  expires through the existing timed-condition lifecycle. This is scoped to
  susceptibility; the global Unconscious condition is unchanged.
- Antimagic remains immediate terminal death under the existing Pit override.
- Netlify publishing remains locked. Validation does not require deployment.

## Maintenance rule

Before starting a family, add its problem, classification, owner, next action,
and acceptance evidence here. Record newly discovered blockers before changing
scope. After each change, regenerate `MONSTER_BLOCKERS_2014.md`; CI checks that
it matches source. After merge, update the operating baseline and verification
on the actual merged commit. Mark an item complete only with its code, permanent
tests, and required exact-head gates; keep the PR and audit links.

- 2026-10-07: Chris replaced row-based weapon choices with legal melee reach, otherwise ranged, highest legal damage; rules contract §10 records this and Gladiator’s fixed shield loadout. M-011 does not include drawn-offhand or random/hit-dependent counts.

M-011 is merged and certified; see the complete sequence audit.

- 2026-10-06: Chris directed us to stop repeatedly checking unchanged code and spend the time building monsters. The operating rule is recorded in AGENTS.md.

M-012 starts from exact main `14f0762205a4267c3cc43291a2ed2fe6bd772f70`. Scope: source-only offhand binding and immutable availability facts; Python/browser sequence resolvers are unchanged. Source wording proves two Longswords plus optional drawn Shortsword, with the strongest compatible fixed loadout selected under §10. One focused parity/source pass, then final-head CI.

M-012 completed #632. Fixed compatible printed offhand preparation follows rules contract §10; native 2024 Warrior Veteran and Half-Dragon were audited independently. Roster gate source-path filter now includes every 2014 monster binder.

## M-013 completion record

#633 completed the Grick family. Narrow missing sequence predicates compose with existing dice, attacks, costs, target/range/line legality, reactions and fresh reset. Source and native 2024 differences are in the Grick audit.

## M-014 completion record

#635 completed printed random sequence repetition through shared dice and ordinary attack resolution. The count is logged and local to one Action, with normal retarget/interruption/fresh reset. Native 2024 Violet Fungus keeps fixed two attacks. Detailed source/lifecycle/parity evidence is in FUNGUS_SEQUENCE_AUDIT.md.

## M-015 completion record

#637 completed the Brass Dragon Sleep Breath family for Wyrmling, Young, and Adult through shared save-area, recharge, timed Unconscious, ends-on-damage, and generic wake-sleeper behavior. Ancient Brass lost the save-action blocker but remains parked on its independent extra-action blocker. The implementation manuals were split into their own merged PR #638 before #637 merged, so combat and documentation ownership remain clean.
