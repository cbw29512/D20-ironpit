# 2014 Stirge Blood Drain source profile

Foundation only. Does not claim admission or remove arena:removed.

## Source (SRD 5.1)

**Blood Drain.** *Melee Weapon Attack:* +5 to hit, reach 5 ft., one creature. *Hit:* 5 (1d4 + 3) piercing damage, and the stirge attaches to the target. While attached, the stirge doesn't attack. Instead, at the start of each of the stirge's turns, the target loses 5 (1d4 + 3) hit points due to blood loss.

The stirge can detach itself by spending 5 feet of its movement. It does so after it drains 10 hit points of blood from the target or the target dies. A creature, including the target, can use its action to detach the stirge.

## Semantic decomposition

- Trigger: melee weapon attack hit
- Immediate: ordinary piercing damage
- State: fight-local attached (source and target linked)
- While attached: source cannot make attacks; instead source-turn-start typed HP loss (1d4+3 piercing, no attack)
- Detach: source spends 5 ft movement; or after 10 HP drained; or target dies; or any creature uses Action (including target)
- Reset: fresh fight clears attachment

## Reuse

Existing `ongoing_damage_effect` on the source card already encodes dice, source_turn_start, blocks_source_attacks, action_removable (5 ft), source_detach_movement_ft, auto_end_after_hp_loss=10.

Universal inventory has `ongoing-periodic-damage` (supported). Inspect Python `on_hit_ongoing_hp_loss` / `grapple_periodic_damage` and browser equivalents before new primitive.

No name dispatch. Python/browser parity required. Tests for attach, tick, detach paths, reset.

## Status

Stirge remains `arena:removed` until the attach lifecycle is fully wired, tested, and exact-head CI passes. Do not weaken fidelity by force-admitting.
