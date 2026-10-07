# Iron Pit context transfer

generated_at: 2026-10-06, after PR #629 merge
main_sha: `58bb5df4c239273588c702ab901775a2d65f0d9e` (merged source baseline; later documentation commits have no combat changes)
active_lane: Complete the 2014 monster roster using one semantic family per PR.

## Authoritative status

[Operating status](CURRENT_OPERATING_STATUS.md); [fix tracker](MONSTER_FIX_TRACKER.md);
[source blockers](MONSTER_BLOCKERS_2014.md). Repository truth overrides this snapshot.

## Active PRs

No active combat PR remained at closeout. #629 is merged; #625 remains closed unmerged reference only.

## Recent merges

[PR #629](https://github.com/cbw29512/D20-ironpit/pull/629): susceptibility binds shared terminal death and timed Stunned;
repairs generated parity and test dependency debt; adds fix tracking with a freshness gate.

## Verified certification

- Source commit: `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`; merged baseline: `58bb5df4c239273588c702ab901775a2d65f0d9e`.
- 2014 monsters 184/327; 2024 monsters 141/330; heroes 240/240 per edition.
- Evidence: regenerated manifests, current source reports, and four exact-head workflows.

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811380): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811451): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811366): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37561811402): success on `9ed5e8fe42dc27ebda4aad0b7843be71f8030171`.

## Current subsystem

- Source data: immutable terminal tags and effect-tag condition grants; incoming action tags.
- Runtime state: existing HP/Dead, timed effects, Concentration, forms, and resources.
- Python path: terminal resolver, effect removal, and shared timed conditions.
- Browser path: terminal effects, effect removal, tagged-condition adapter, and shared timed conditions.
- Generated path: normal capability and browser exporters; no hand-edited generated data.
- Tests: susceptibility, terminal lifecycle, Dispel lifecycle, and all permanent CI suites.
- Edition: exact 2014 family only; native 2024 constructs do not print susceptibility.

## Open A-class correctness debt

None remains in the touched susceptibility subsystem. The 143 remaining 2014 source
monsters remain blocked, including the rug's independent Damage Transfer/attack debt;
see the generated list. Do not interpret the roster count as full completion.

## Open B-class architecture debt

None remains in the touched subsystem. The next family requires semantic reuse classification.

## Parked C-class cleanup

Unrelated cosmetic cleanup and art/presentation remain outside this mechanic lane.

## Locked decisions

Rules contract §13 Antimagic susceptibility: antimagic is terminal; Dispel applies
shared Stunned for 10 rounds with unchanged HP and no save. This is a scoped Pit
override. Publishing remains locked.

## Next exact action

Classify the remaining 2014 blocker families against existing hero and monster primitives.

## Do not carry forward

Old counts, prior-head CI, #625 code without revalidation, or chat-only rule decisions.
Re-anchor main, open PRs, and workflow evidence before the next implementation.
