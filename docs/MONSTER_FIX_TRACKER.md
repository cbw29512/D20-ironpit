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
| P1 M-006 | Next: M-011 | Remaining 2014 source roster is incomplete. | Generated blockers are current after #630. Audit alternative-count Multiattack next; do not combine unrelated trait families. |
| P1 M-007 | Audited for #629/#630 | Check 2024 source reuse without inventing matching traits. | Native 2024 constructs have no susceptibility; all 330 native trait texts lack the included weapon traits. No 2014 trait/qualifier copied. Repeat per family. |
| P1 D-001 | Complete | Operating status still referenced PR #624 and 177/327 despite newer main. | Current merged baseline and final-head verification recorded below and in operating status. |
| P1 M-008 | Complete, merged #630 | Seven 2014 source traits already include their damage: Brute (Bugbear/Gladiator), Heated Weapons (Azer/Salamander), Angelic Weapons (Deva/Planetar/Solar). | Pinned source validation, shared typed damage/magical qualifier, critical/defense/reset parity, and all four exact-head gates passed. Seven traits resolved; other card blockers remain. [Audit](INCLUDED_WEAPON_DAMAGE_AUDIT.md). |
| P1 M-009 | Deferred, separate contact tranche | Heated Body triggers on touching or a melee hit within 5 feet; current retaliation handles only melee hits. | Reuse retaliation damage and add a shared contact trigger only after schema audit. Azer/Salamander/Remorhaz remain blocked. |
| P1 M-010 | Deferred, separate grapple tranche | Salamander Tail automatically hits its own grappled target and cannot attack others; current policy lacks automatic hit. | Preserve source `auto_hit_own_grapple`; do not replace automatic hit with Advantage. |
| P1 M-011 | Active, ChatGPT; `fix/2014-multiattack-sequences` | Gladiator now has only alternative-count Multiattack left (three melee or two ranged attacks). Bandit Captain is a related paired catch-up candidate. | ENGINE_EXISTS_PARAMETER_DELTA: extend shared slots with complete alternatives for Bandit Captain, Gladiator, Medusa, and distinct-weapon Lizardfolk. Legal melee reach selects mode; highest damage selects legal choices. Shield stays equipped. Source/preview/resolution parity and native 2024 audit required. |

## Current evidence

Merged source baseline: `35684e3d0ae9dd745a62722617ceed23c6d43ef3` from [PR #630](https://github.com/cbw29512/D20-ironpit/pull/630).
Verified source head: `a9e229601cdce17ecb6cb856a4f8be85e69fbd05`. All four required exact-head gates passed before
merge. Recomputed merged-source reports and manifest verification retain 184/327
2014 monsters, 141/330 2024 monsters, and 240/240 heroes per edition. All 143
blocked 2014 cards remain blocked; seven included weapon traits are now bound.
CI passed 2,730 Python tests and all 218 browser regression commands. Local full
Python passed 2,729 tests; the final 63-test focused run includes the added fixture
freshness test. [Detailed audit](INCLUDED_WEAPON_DAMAGE_AUDIT.md).

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37564118269): success on `a9e229601cdce17ecb6cb856a4f8be85e69fbd05`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37564118283): success on `a9e229601cdce17ecb6cb856a4f8be85e69fbd05`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37564118297): success on `a9e229601cdce17ecb6cb856a4f8be85e69fbd05`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37564118259): success on `a9e229601cdce17ecb6cb856a4f8be85e69fbd05`.

These links verify the stated source head. Later documentation-only commits do
not inherit its exact-head CI status. The earlier #629 evidence remains in its
[susceptibility audit](ANTIMAGIC_SUSCEPTIBILITY_AUDIT.md).

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

M-011 schema/source/parity evidence: [Complete sequence audit](MULTIATTACK_SEQUENCE_AUDIT.md). Branch counts are 187/327 admitted/compiled; required exact-head CI remains pending.
