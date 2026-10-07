# Monster fix tracker

Updated 2026-10-06. Owner: ChatGPT for combat mechanics; Grok retains art/presentation ownership.

This is the maintained work queue. [Every blocked 2014 monster](MONSTER_BLOCKERS_2014.md)
is generated from current source; [current operating status](CURRENT_OPERATING_STATUS.md)
sets the work lane. Rules live in the rules contract, not this tracker.

## Active and deferred fixes

| Priority / ID | Status | Problem and scope | Next action / completion evidence |
|---|---|---|---|
| P0 M-001 | Active, PR #629 | Complete 2014 Antimagic Susceptibility for Animated Armor, Flying Sword, and Rug of Smothering. Dispel uses existing Stunned for 10 rounds; antimagic uses shared terminal death. | Finish Python/browser parity and lifecycle regressions; regenerate data; require all four exact-head gates. [Detailed audit](ANTIMAGIC_SUSCEPTIBILITY_AUDIT.md). |
| P0 M-002 | Active, part of #629 | Stale capability export and browser bundle caused resumed-head CI failure. | Regenerate from the branch; run export freshness checks and browser sentinel tests. Prior CI success is not final-head evidence. |
| P0 M-003 | Active, part of #629 | Terminal resolver extraction left three browser test loaders missing their production dependency. | Load the shared terminal runtime in those regressions; rerun all CI browser commands. |
| P0 M-004 | Active, part of #629 | Touched Stunned primitive omitted 2014 movement restriction. | Reuse edition-aware condition speed predicate in both runtimes; retain existing Stunned combat semantics. |
| P1 M-005 | Deferred | Rug of Smothering remains blocked by attack representation, extra action, and Damage Transfer. | Audit each behavior and classify reuse before implementation. Susceptibility alone does not certify the rug. |
| P1 M-006 | Queued after #629 | Remaining 2014 source roster is incomplete. | Recompute the generated blocker list after merge; choose the largest coherent semantic family that maps to one shared primitive. Do not batch all `source:trait` mechanics together. |
| P1 M-007 | Audited for this family | Check 2024 source reuse without inventing matching traits. | Native 2024 animated armor/sword/rug have no Antimagic Susceptibility; no binding added. Repeat the edition audit for each subsequent family. |
| P1 D-001 | Active | Operating status still referenced PR #624 and 177/327 despite newer main. | Record main SHA and distinguish merged counts, branch source counts, local tests, and exact-head gates. |

## Current evidence

Starting main: `27ab34be9ac96642015ed1af9c62ea683074f3e1`.
Resumed PR head: `81ff8ca871b89827ecfff4c160a2a3af601d64ba`.
That head passed three certification workflows but failed CI. Working changes
are not yet a final commit or a green-gates claim. Source classification on this
branch admits 184/327 2014 monsters; 2024 remains 141/330. Both hero editions
remain 240/240. Refresh verification below when the final branch is tested.

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
