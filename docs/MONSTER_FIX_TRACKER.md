# Monster fix tracker

Updated 2026-10-06. Owner: ChatGPT for combat mechanics; Grok retains art/presentation ownership.

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
| P1 M-006 | Queued after #629 | Remaining 2014 source roster is incomplete. | Recompute the generated blocker list after merge; choose the largest coherent semantic family that maps to one shared primitive. Do not batch all `source:trait` mechanics together. |
| P1 M-007 | Audited for this family | Check 2024 source reuse without inventing matching traits. | Native 2024 animated armor/sword/rug have no Antimagic Susceptibility; no binding added. Repeat the edition audit for each subsequent family. |
| P1 D-001 | Complete | Operating status still referenced PR #624 and 177/327 despite newer main. | Current merged baseline and final-head verification recorded below and in operating status. |

## Current evidence

Merged source baseline: `58bb5df4c239273588c702ab901775a2d65f0d9e` from [PR #629](https://github.com/cbw29512/D20-ironpit/pull/629).
Verified source head: `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`. All four required exact-head gates passed before
merge. Certification is 184/327 2014 monsters, 141/330 2024 monsters, and 240/240
heroes per edition. The generated list retains all 143 blocked 2014 monsters.
All 217 browser regression commands passed locally and in CI. Full Python CI
passed on the final source head; the focused Dispel tests also cover lifecycle
and concentration cleanup.

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811380): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811451): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811366): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811402): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.

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
