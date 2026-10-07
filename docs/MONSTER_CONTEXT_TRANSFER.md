# Iron Pit context transfer

generated_at: 2026-10-07, after PR #630 merge
main_sha: `35684e3d0ae9dd745a62722617ceed23c6d43ef3` (merged source baseline; subsequent closeout documentation changes no combat source)
active_lane: Complete 2014 source monsters, one semantic family per PR.

## Authoritative status

[Operating status](CURRENT_OPERATING_STATUS.md), [fix tracker](MONSTER_FIX_TRACKER.md),
[generated blockers](MONSTER_BLOCKERS_2014.md), and [current audit](INCLUDED_WEAPON_DAMAGE_AUDIT.md).
Repository truth overrides this cache. Netlify is locked; Grok owns art/presentation.

## Active PRs

No active combat PR remains; #630 is merged. Refetch open PRs and exact current
main before new work; this packet is a cache of the stated source baseline.

## Recent merges

#630 included weapon traits is merged after all gates. #629 susceptibility is
complete. #625 remains closed unmerged reference only.

## Verified certification

Recomputed against the actual merged source baseline using source/paired reports and generated
manifest verification: 184/327 2014 monsters, 141/330 2024 monsters, 240/240 heroes
per edition. All 143 blocked 2014 cards remain blocked. No promotion in this batch.
Verified source head: `a9e229601cdce17ecb6cb856a4f8be85e69fbd05`; all four required gates passed,
including 2,730 Python tests and 218 browser commands. Exact workflow links are
in the fix tracker. Later documentation-only commits do not inherit its CI status.

## Current subsystem

- Immutable source: printed trait/action text, base damage and typed on-hit riders.
- Runtime state: existing temporary fight HP/audit; no new state or lifecycle.
- Python: generic attack compiler, damage components, conditional defenses.
- Browser: production attack/mixed damage and conditional defenses.
- Generated path: ordinary runtime/static exporters and blocker list generator.
- Tests: source/compiler test and source-derived Python/browser parity fixture.
- Edition: 2014 bindings only; no matching native 2024 traits were found.

## Open A-class correctness debt

No A-class debt remains in the touched binding subsystem. The Angelic magical
qualifier omission is fixed and verified in both engines.
Printed included dice are validated without adding a second damage grant.
Other card mechanics remain fail-closed, including Surprise Attack, Heated Body,
Salamander Tail automatic hit, multiattack choice, spells/healing/forms/legendary
options. See M-005/M-009/M-010 and generated blockers; do not strip those mechanics.

## Open B-class architecture debt

The source model now retains action text for independent payload validation.
No duplicated resolver or new combat primitive is introduced.

## Parked C-class cleanup

Unrelated cosmetics/art/presentation remain outside this lane.

## Locked decisions

Rules contract §13: susceptibility Dispel is existing Stunned for 10 rounds,
unchanged HP/no save; antimagic is terminal. Global Unconscious is unchanged.
This batch introduces no new rules interpretation.

## Next exact action

Re-anchor exact main/open work, then audit alternative-count Multiattack for
Gladiator and Bandit Captain against shared action-slot/selection primitives (M-011).

## Do not carry forward

Stale counts, previous-head workflow success, closed #625 code, or chat-only decisions.
