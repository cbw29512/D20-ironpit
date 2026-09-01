from app.combat.concentration import end_concentration, start_concentration
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.ongoing_spell_control import apply_ongoing_spell_condition, forced_retreat_active
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup


class NoRollDice:
    def roll(self, sides: int) -> int:
        raise AssertionError(f"Forced-retreat turn unexpectedly rolled d{sides}.")


def _member(combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _target() -> EncounterCombatant:
    return _member("fighter", "heroes", 5)


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


def test_forced_retreat_skips_voluntary_turn_without_moving_card() -> None:
    fighter = _target()
    enemy = _member("goblin", "monsters", 10)
    setup = EncounterSetup(heroes=[fighter], monsters=[enemy], hero_total_levels=1, monster_total_cr="1")
    apply_ongoing_spell_condition(
        fighter.state, "frightened", "shaman", "fear", "wisdom", 13,
        applied_round=1, turn_behavior="forced_retreat",
    )
    before = fighter.position_ft
    events, _ = resolve_combat_turn(1, 1, fighter, enemy, setup, NoRollDice())
    assert fighter.position_ft == before
    assert forced_retreat_active(fighter.state) is True
    assert [event.feature_id for event in events] == ["forced-retreat"]
    assert not any(event.event_type in {"attack", "healing", "movement"} for event in events)

    save_events, _ = resolve_target_condition_timing(
        2, 1, fighter, "target_turn_end", FixedDiceProvider([20]),
    )
    assert save_events[0].save_succeeded is True
    assert save_events[0].removed_condition_ids == ["frightened"]
    assert forced_retreat_active(fighter.state) is False


def test_lost_concentration_removes_control_condition_and_retreat_behavior() -> None:
    caster = _member("shaman", "monsters", 15)
    target = _target()
    states = [caster.state, target.state]
    start_concentration(caster.state, "shaman", "fear", 1, states, expires_round=11)
    apply_ongoing_spell_condition(
        target.state, "frightened", "shaman", "fear", "wisdom", 13,
        applied_round=1, turn_behavior="forced_retreat", affected_states=states,
    )
    assert forced_retreat_active(target.state) is True
    assert "frightened" in target.state.active_effect_ids

    assert end_concentration(caster.state, states) is True
    assert caster.state.concentration is None
    assert target.state.timed_effects == []
    assert "frightened" not in target.state.active_effect_ids
    assert forced_retreat_active(target.state) is False
