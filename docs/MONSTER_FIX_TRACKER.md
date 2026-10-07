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
| P1 M-006 | Next: M-012 | Remaining 2014 source roster is incomplete. | Generated blockers are current after #631: 187/327 READY, 140 blocked. Continue source bindings through certified primitives. |
| P1 M-007 | Audited for #629/#630 | Check 2024 source reuse without inventing matching traits. | Native 2024 constructs have no susceptibility; all 330 native trait texts lack the included weapon traits. No 2014 trait/qualifier copied. Repeat per family. |
| P1 D-001 | Complete | Operating status still referenced PR #624 and 177/327 despite newer main. | Current merged baseline and final-head verification recorded below and in operating status. |
| P1 M-008 | Complete, merged #630 | Seven 2014 source traits already include their damage: Brute (Bugbear/Gladiator), Heated Weapons (Azer/Salamander), Angelic Weapons (Deva/Planetar/Solar). | Pinned source validation, shared typed damage/magical qualifier, critical/defense/reset parity, and all four exact-head gates passed. Seven traits resolved; other card blockers remain. [Audit](INCLUDED_WEAPON_DAMAGE_AUDIT.md). |
| P1 M-009 | Deferred, separate contact tranche | Heated Body triggers on touching or a melee hit within 5 feet; current retaliation handles only melee hits. | Reuse retaliation damage and add a shared contact trigger only after schema audit. Azer/Salamander/Remorhaz remain blocked. |
| P1 M-010 | Deferred, separate grapple tranche | Salamander Tail automatically hits its own grappled target and cannot attack others; current policy lacks automatic hit. | Preserve source `auto_hit_own_grapple`; do not replace automatic hit with Advantage. |
| P1 M-011 | Complete, merged #631 | Gladiator now has only alternative-count Multiattack left (three melee or two ranged attacks). Bandit Captain is a related paired catch-up candidate. | Complete source alternatives bind Bandit Captain, Gladiator, Lizardfolk, and Medusa. First three are READY; Medusa retains Petrifying Gaze. Highest legal damage/reach policy, fixed shield, parity and all gates passed. [Audit](MULTIATTACK_SEQUENCE_AUDIT.md). |

| P1 M-012 | Active, ChatGPT; `feat/2014-veteran-multiattack` | Veteran and Half-Red Dragon Veteran: two Longsword attacks plus conditional drawn Shortsword; two-handed Longsword is incompatible with held offhand. | Source binding complete; focused source/parity checks passed (25 Python cases across the changed family and reused shield/source helpers; four browser parity cases). Generated branch roster 189/327, 138 blocked. Ranged Crossbow is a standalone action. Required final-head CI pending. |
| P1 D-002 | Complete, Chris decision | Repeated broad verification displaced monster construction. | AGENTS.md records one focused changed-family pass and one final-head CI pass; no duplicate full local suites. |

## Current evidence

Merged source baseline: `7c1199a4a4d1c6241b472bc28eadb235d58b8910` from [PR #631](https://github.com/cbw29512/D20-ironpit/pull/631).
Verified feature head: `7034cf80341cb842c04a1b90a028e33cdb5525ad`. All four required exact-head gates passed.
2014 monsters: **187/327 READY**, **140 blocked**. Native 2024: **141/330**.
Heroes: **240/240** per edition. CI passed **2,760 Python tests** and **219 browser
commands**; the final local focused pass covered 133 tests. Source/runtime/browser
manifests agree. [Detailed sequence audit](MULTIATTACK_SEQUENCE_AUDIT.md).

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999836): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999753): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999736): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37567999745): success on `7034cf80341cb842c04a1b90a028e33cdb5525ad`.

These links verify the stated source head. Subsequent documentation-only commits
have no inherited exact-head CI claim. Historical #629/#630 evidence remains in
their susceptibility/included-weapon audits.

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
