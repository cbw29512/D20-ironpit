# Iron Pit context transfer

generated_at: 2026-10-07, included weapon damage implementation
main_sha: `b63cbfb2e2432b1f8c37fb365500c895f4efb08e`
active_lane: Complete 2014 source monsters, one semantic family per PR.

## Authoritative status

[Operating status](CURRENT_OPERATING_STATUS.md), [fix tracker](MONSTER_FIX_TRACKER.md),
[generated blockers](MONSTER_BLOCKERS_2014.md), and [current audit](INCLUDED_WEAPON_DAMAGE_AUDIT.md).
Repository truth overrides this cache. Netlify is locked; Grok owns art/presentation.

## Active PRs

No open PR at branch creation. Local branch `fix/2014-included-weapon-traits`
contains source validation and magical qualifier binding; head CI is pending.

## Recent merges

#629 susceptibility is merged. #625 remains closed unmerged reference only.

## Verified certification

Recomputed against current branch source using source/paired reports and generated
manifest verification: 184/327 2014 monsters, 141/330 2024 monsters, 240/240 heroes
per edition. All 143 blocked 2014 cards remain blocked. No promotion in this batch.
Prior-head workflow evidence applies only to the SHA recorded in the fix tracker;
all new exact-head gates are pending.

## Current subsystem

- Immutable source: printed trait/action text, base damage and typed on-hit riders.
- Runtime state: existing temporary fight HP/audit; no new state or lifecycle.
- Python: generic attack compiler, damage components, conditional defenses.
- Browser: production attack/mixed damage and conditional defenses.
- Generated path: ordinary runtime/static exporters and blocker list generator.
- Tests: source/compiler test and source-derived Python/browser parity fixture.
- Edition: 2014 bindings only; no matching native 2024 traits were found.

## Open A-class correctness debt

Angelic magical qualifier omission is fixed in the branch, awaiting all gates.
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

Finish full verification, publish the coherent PR, and require all four exact-head gates.

## Do not carry forward

Stale counts, previous-head workflow success, closed #625 code, or chat-only decisions.
