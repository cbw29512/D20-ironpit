from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.ongoing_spell_control import apply_ongoing_spell_condition
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant


def _target() -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id="fighter", side="heroes", position_ft=5,
        state=build_combatant_state(build_karnok_stoneward()),
    )


def test_ongoing_spell_control_repeats_same_save_at_target_turn_end() -> None:
    target = _target()
    applied = apply_ongoing_spell_condition(
        target.state, "frightened", "shaman", "fear", "wisdom", 13, applied_round=1,
    )
    assert applied == "frightened"
    assert target.state.active_effect_ids == ["frightened"]
    effect = target.state.timed_effects[0]
    assert effect.source_effect_id == "fear"
    assert effect.repeat_save_ability == "wisdom"
    assert effect.repeat_save_dc == 13
    assert effect.repeat_save_timing == "target_turn_end"

    events, sequence = resolve_target_condition_timing(
        1, 1, target, "target_turn_end", FixedDiceProvider([20]),
    )
    assert sequence == 2
    assert len(events) == 1
    assert events[0].save_succeeded is True
    assert events[0].removed_condition_ids == ["frightened"]
    assert "frightened" not in target.state.active_effect_ids
    assert target.state.timed_effects == []


def test_failed_repeat_save_keeps_ongoing_spell_condition_active() -> None:
    target = _target()
    apply_ongoing_spell_condition(
        target.state, "frightened", "shaman", "fear", "wisdom", 30, applied_round=1,
    )
    events, _ = resolve_target_condition_timing(
        1, 1, target, "target_turn_end", FixedDiceProvider([1]),
    )
    assert events[0].save_succeeded is False
    assert events[0].removed_condition_ids == []
    assert "frightened" in target.state.active_effect_ids
    assert len(target.state.timed_effects) == 1
