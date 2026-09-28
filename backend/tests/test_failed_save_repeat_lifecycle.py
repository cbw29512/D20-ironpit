from __future__ import annotations

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant
from app.domain.save_effects import FailedSaveTimedEffect


def _member(cid: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=cid,
        side=side,
        position_ft=0,
        state=build_combatant_state(build_karnok_stoneward().model_copy(deep=True)),
    )


def test_failed_save_timed_effect_can_repeat_save_until_duration_expires() -> None:
    actor = _member("source", "heroes")
    target = _member("target", "monsters")
    action = SavingThrowAction(
        id="fear-effect",
        name="Fear Effect",
        save_ability="wisdom",
        dc=18,
        range_ft=30,
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="frightened",
            expiry_timing="target_turn_end",
            duration_rounds=10,
            repeat_save_ability="wisdom",
            repeat_save_dc=18,
            repeat_save_timing="target_turn_end",
        ),
    )

    event = resolve_save_action(1, 1, actor, target, action, 5, FixedDiceProvider([1]), spend_action=False)
    assert event.save_succeeded is False
    effect = target.state.timed_effects[0]
    assert effect.effect_id == "frightened"
    assert effect.expires_round == 11
    assert effect.repeat_save_ability == "wisdom"
    assert effect.repeat_save_dc == 18
    assert effect.repeat_save_timing == "target_turn_end"

    events, _ = resolve_target_condition_timing(2, 1, target, "target_turn_end", FixedDiceProvider([1]))
    assert events[0].save_succeeded is False
    assert "frightened" in target.state.active_effect_ids

    events, _ = resolve_target_condition_timing(3, 2, target, "target_turn_end", FixedDiceProvider([20]))
    assert events[0].save_succeeded is True
    assert "frightened" not in target.state.active_effect_ids


def test_failed_save_repeat_schema_requires_complete_repeat_triplet() -> None:
    try:
        FailedSaveTimedEffect(effect_id="frightened", repeat_save_ability="wisdom")
    except ValueError:
        return
    raise AssertionError("partial failed-save repeat lifecycle must fail closed")
