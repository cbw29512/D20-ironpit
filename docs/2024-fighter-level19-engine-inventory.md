# 2024 Champion Fighter level 19 engine inventory

## Authoritative RAW anchor

D&D Beyond Basic Rules 2024, Fighter Features table: Fighter 19 gains **Epic Boon**; the class text recommends **Boon of Combat Prowess**.

D&D Beyond Basic Rules 2024, Boon of Combat Prowess:

- Ability Score Increase: increase one ability score by 1, maximum 30.
- Peerless Aim: when an attack roll misses, the character can make it hit instead; after use, it cannot be used again until the start of the character's next turn.

## State/data first

The canonical Karnok level-19 snapshot must inherit the certified level-18 state and represent the feat as data. It must not become READY until the selected ability increase and Peerless Aim are both represented and audited.

Required reusable combat state for Peerless Aim:

- trigger: attack-roll miss
- effect: convert that miss to a hit
- recharge boundary: start of actor's next turn
- availability: one use between recharge boundaries

This is not Fighter-specific behavior. Any future feature with the same core trigger/effect/recharge semantics must reuse the same universal capability even if its feature name differs.

## Existing-engine comparison

Repository search on main `eeef9b1a5cef097185309d3328631ed7509a4d79` found no existing `Boon of Combat Prowess`, `Peerless Aim`, or generic miss-to-hit / once-until-start-of-next-turn capability that can be safely claimed for certification.

Therefore level 19 is technically blocked on one genuinely reusable engine primitive: **miss-to-hit conversion with start-of-next-turn recharge**. Do not implement a Karnok-name or Fighter-name branch.

The +1 ability score portion should reuse the existing canonical stat/feat progression machinery if its max-30 Epic Boon cap is already representable; otherwise extend that data-driven cap rather than adding a Fighter special case.

## Required implementation/certification coverage

Before Karnok L19 can earn READY:

1. Add a data schema for the reusable miss-to-hit capability and its recharge semantics.
2. Add Python runtime resolution and structured logging for availability, conversion, consumption, and recharge.
3. Add browser runtime parity using the same data contract.
4. Add Python tests proving miss conversion, consumption, no second conversion before recharge, and recharge at start of next turn.
5. Add browser parity tests for the same state transitions.
6. Add certification capability support so READY is earned from executable behavior.
7. Build the L19 canonical profile from certified L18, apply the Epic Boon ASI legally, and attach Boon of Combat Prowess audit/source data.
8. Regenerate authoritative manifests/artifacts through the normal generator; never hand-edit READY/counts.

## Edition separation

This inventory is 2024-only. No 2014 profile receives Epic Boon or Peerless Aim from this work. A universal primitive may be shared by engine code, but activation remains entirely data-driven by edition-specific content.
