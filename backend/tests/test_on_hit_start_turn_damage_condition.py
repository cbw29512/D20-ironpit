"""Universal on-hit timed condition with start-of-turn typed damage."""
from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.start_of_turn_save_condition_events import (
    resolve_start_of_turn_save_condition_damage_events,
)
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons import OnHitConditionSave
from test_on_hit_condition_save import _attacker, _target


def _fight():
    try:
        effect = OnHitConditionSave(
            save_ability="constitution",
            dc=21,
            condition_id="poisoned",
            repeat_save_timing="target_turn_end",
            cannot_regain_hit_points=True,
            start_of_turn_damage_dice_count=6,
            start_of_turn_damage_dice_size=6,
            start_of_turn_damage_type="poison",
        )
        attacker_state, attack = _attacker(effect)
        target_state = _target(save_ability="constitution")
        attacker = EncounterCombatant(
            combatant_id="renamed-source",
            side="monsters",
            position_ft=0,
            state=attacker_state,
        )
        target = EncounterCombatant(
            combatant_id="renamed-target",
            side="heroes",
            position_ft=5,
            state=target_state,
        )
        return attacker, target, attack, EncounterSetup(heroes=[target], monsters=[attacker])
    except Exception as exc:
        raise AssertionError("Failed to build start-turn condition test fight.") from exc


def test_failed_save_stores_generic_poison_lifecycle_and_blocks_healing():
    attacker, target, attack, setup = _fight()

    event = resolve_attack(
        1, 1, attacker.state, target.state, attack, 5,
        FixedDiceProvider([15, 4, 4, 1]),
        spend_action=False,
        actor_event_id=attacker.combatant_id,
        target_event_id=target.combatant_id,
        reaction_setup=setup,
    )

    assert event.hit is True and event.save_succeeded is False
    effect = next(item for item in target.state.timed_effects if item.effect_id == "poisoned")
    assert effect.cannot_regain_hit_points is True
    assert effect.repeat_save_ability == "constitution"
    assert effect.repeat_save_dc == 21
    assert effect.repeat_save_timing == "target_turn_end"
    assert effect.start_of_turn_dice_count == 6
    assert effect.start_of_turn_dice_size == 6
    assert str(effect.start_of_turn_damage_type) == "poison"

    before = target.state.current_hp
    restore_hit_points(target.state, 10)
    assert target.state.current_hp == before


def test_start_turn_damage_uses_typed_damage_then_end_turn_save_removes_effect():
    attacker, target, attack, setup = _fight()
    resolve_attack(
        1, 1, attacker.state, target.state, attack, 5,
        FixedDiceProvider([15, 4, 4, 1]),
        spend_action=False,
        actor_event_id=attacker.combatant_id,
        target_event_id=target.combatant_id,
        reaction_setup=setup,
    )
    hp_before = target.state.current_hp

    events, sequence = resolve_start_of_turn_save_condition_damage_events(
        2, 2, target, setup, FixedDiceProvider([1, 1, 1, 1, 1, 1]),
    )

    assert sequence == 3
    assert len(events) == 1
    assert events[0].hp_before == hp_before
    assert events[0].hp_after == hp_before - 6
    assert "6 poison damage" in events[0].description
    assert "poisoned" in target.state.active_effect_ids

    recovered, _ = resolve_target_condition_timing(
        3, 2, target, "target_turn_end", FixedDiceProvider([20]), setup,
    )
    assert recovered[0].save_succeeded is True
    assert "poisoned" not in target.state.active_effect_ids
    assert not target.state.timed_effects
