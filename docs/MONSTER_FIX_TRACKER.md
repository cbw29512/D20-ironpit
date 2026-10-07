# Monster fix tracker

Updated 2026-10-07. Owner: ChatGPT for combat mechanics; Grok retains art/presentation ownership.

This is the maintained work queue. [Every blocked 2014 monster](MONSTER_BLOCKERS_2014.md)
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
| P1 M-006 | Next: M-014 | Remaining 2014 source roster is incomplete. | Generated blockers are current after #633: 190/327 READY, 137 blocked. Continue source bindings through certified primitives. |
| P1 M-007 | Audited for #629/#630 | Check 2024 source reuse without inventing matching traits. | Native 2024 constructs have no susceptibility; all 330 native trait texts lack the included weapon traits. No 2014 trait/qualifier copied. Repeat per family. |
| P1 D-001 | Complete | Operating status still referenced PR #624 and 177/327 despite newer main. | Current merged baseline and final-head verification recorded below and in operating status. |
| P1 M-008 | Complete, merged #630 | Seven 2014 source traits already include their damage: Brute (Bugbear/Gladiator), Heated Weapons (Azer/Salamander), Angelic Weapons (Deva/Planetar/Solar). | Pinned source validation, shared typed damage/magical qualifier, critical/defense/reset parity, and all four exact-head gates passed. Seven traits resolved; other card blockers remain. [Audit](INCLUDED_WEAPON_DAMAGE_AUDIT.md). |
| P1 M-009 | Deferred, separate contact tranche | Heated Body triggers on touching or a melee hit within 5 feet; current retaliation handles only melee hits. | Reuse retaliation damage and add a shared contact trigger only after schema audit. Azer/Salamander/Remorhaz remain blocked. |
| P1 M-010 | Deferred, separate grapple tranche | Salamander Tail automatically hits its own grappled target and cannot attack others; current policy lacks automatic hit. | Preserve source `auto_hit_own_grapple`; do not replace automatic hit with Advantage. |
| P1 M-011 | Complete, merged #631 | Gladiator now has only alternative-count Multiattack left (three melee or two ranged attacks). Bandit Captain is a related paired catch-up candidate. | Complete source alternatives bind Bandit Captain, Gladiator, Lizardfolk, and Medusa. First three are READY; Medusa retains Petrifying Gaze. Highest legal damage/reach policy, fixed shield, parity and all gates passed. [Audit](MULTIATTACK_SEQUENCE_AUDIT.md). |

| P1 M-012 | Complete, merged #632 | Veteran and Half-Red Dragon Veteran: two Longsword attacks plus conditional drawn Shortsword; two-handed Longsword is incompatible with held offhand. | Source-only binding, 25 focused Python cases, four browser parity cases, and all four exact-head gates passed. Ranged Crossbow stays one standard attack; AC/breath preserved. [PR #632](https://github.com/cbw29512/D20-ironpit/pull/632); [audit](MULTIATTACK_SEQUENCE_AUDIT.md). |
| P1 D-002 | Complete, Chris decision | Repeated broad verification displaced monster construction. | AGENTS.md records one focused changed-family pass and one final-head CI pass; no duplicate full local suites. |

| P1 M-013 | Complete, merged #633 | Tentacles hit permits one Beak attack against the same target. The source policy is still fail-closed `multiattack:complex`. | Generic previous-hit/actual-target requirements bind Grick. 58 focused Python cases, eight browser scenarios, and all four final-head gates passed. [Audit](GRICK_SEQUENCE_AUDIT.md). |
| P1 M-014 | Active, ChatGPT; `feat/2014-violet-fungus-repeat` | Violet Fungus rolls 1d4 Rotting Touch attacks. | Generic repetition/shared dice binding complete; 70 focused Python cases, seven new browser scenarios and affected prior fixtures passed. Generated branch 191/327, 136 blocked; final-head CI pending. |

## Current evidence

Merged source baseline: `72d4a8d3e1aec7d9e70bc9154ec6f03e3cfc0e64` from [PR #633](https://github.com/cbw29512/D20-ironpit/pull/633).
Verified feature head: `d3c8021d125e2a9f4aa001db89d2cca9758fca6f`. All four required exact-head gates passed.
2014 monsters **190/327 READY**, **137 blocked**; native 2024 **141/330**; heroes **240/240** each edition.
CI: **2,788 Python tests**, **221 browser commands**. Local focused proof: 58 Python cases and eight new browser parity scenarios. Generated source/runtime/browser certification agrees. Initial serializer package-import collection failure was corrected; no full local suite was duplicated.

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37571348122): success on `d3c8021d125e2a9f4aa001db89d2cca9758fca6f`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37571348071): success on `d3c8021d125e2a9f4aa001db89d2cca9758fca6f`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37571348171): success on `d3c8021d125e2a9f4aa001db89d2cca9758fca6f`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37571348073): success on `d3c8021d125e2a9f4aa001db89d2cca9758fca6f`.

These verify the feature head; later documentation-only successors do not inherit its exact-head CI result.

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

## M-014 active build (2026-10-07)

Owner ChatGPT; branch `feat/2014-violet-fungus-repeat`, anchored to merged #633 closeout main `8a5d37360aaf49f65198f4b145fe32a5af42e251`. Source: Violet Fungus makes 1d4 Rotting Touch attacks. Shared dice pools, ordinary repeated slot resolution/costs/retarget/interruption/reset exist; immutable random whole-sequence repetition is missing (`ENGINE_TRULY_MISSING` only for that sequence parameter/expansion). Reuse the ordinary dice service and attack loop; no creature-name resolver. Focused acceptance: each d4 result 1–4, natural 1 interruption, retarget after a kill, out-of-range/no-spend/no-roll, fresh count next fight, preview purity, malformed source/schema fail-closed, Python/browser parity. Native 2024 audited independently.
