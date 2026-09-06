from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.simple_monster_source_definitions import build_simple_source_definitions
from app.domain.models import EncounterCombatant, SaveConditionEffect, SavingThrowAction


def _combatant(combatant_id: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="monsters" if position_ft == 0 else "heroes",
        position_ft=position_ft,
        state=build_combatant_state(build_goblin_warrior()),
    )


def test_failed_save_applies_source_bound_timed_condition() -> None:
    actor = _combatant("monster-1:source", 0)
    target = _combatant("hero-1:target", 5)
    action = SavingThrowAction(
        id="test-charm", name="Test Charm", save_ability="wisdom", dc=20, range_ft=30,
        failure_conditions=[SaveConditionEffect(condition_id="charmed", expiry_timing="source_turn_start")],
    )

    event = resolve_save_action(1, 1, actor, target, action, 5, FixedDiceProvider([1]))

    assert event.save_succeeded is False
    assert event.applied_condition_ids == ["charmed"]
    assert "charmed" in target.state.active_effect_ids
    effect = target.state.timed_effects[0]
    assert effect.source_id == actor.combatant_id
    assert effect.source_effect_id == action.id
    assert effect.expiry_timing == "source_turn_start"


def test_successful_save_does_not_apply_condition() -> None:
    actor = _combatant("monster-1:source", 0)
    target = _combatant("hero-1:target", 5)
    action = SavingThrowAction(
        id="test-charm", name="Test Charm", save_ability="wisdom", dc=2, range_ft=30,
        failure_conditions=[SaveConditionEffect(condition_id="charmed", expiry_timing="source_turn_start")],
    )

    event = resolve_save_action(1, 1, actor, target, action, 5, FixedDiceProvider([20]))

    assert event.save_succeeded is True
    assert event.applied_condition_ids == []
    assert target.state.timed_effects == []


def test_pirate_source_builds_one_panache_replacement_slot() -> None:
    definition = build_simple_source_definitions()["srd-pirate"]
    panache = next(action for action in definition.save_actions if action.name == "Enthralling Panache")

    assert panache.save_ability == "wisdom"
    assert panache.dc == 12
    assert panache.range_ft == 30
    assert panache.failure_conditions[0].condition == "charmed"
    assert panache.failure_conditions[0].expiry_timing == "source_turn_start"
    assert definition.attack_action is not None
    save_slots = [slot for slot in definition.attack_action.slots if panache.id in slot.save_action_ids]
    assert len(save_slots) == 1
    assert len(definition.attack_action.slots) == 2
