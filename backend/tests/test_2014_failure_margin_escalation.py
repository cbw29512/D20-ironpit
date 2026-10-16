"""Source-neutral failed-save margin escalation parity and lifecycle regressions."""
from __future__ import annotations

import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.source_bound_effects import end_damage_sensitive_effects
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.failure_margin import FailureMarginEscalation
from app.domain.weapons import OnHitConditionSave


def _strike(save_roll: int, *, duration_die: int | None = None, name: str = "Synthetic Sting"):
    try:
        attacker = build_combatant_state(
            build_karnok_stoneward().model_copy(update={"combat_traits": []}, deep=True)
        )
        target_source = build_goblin_warrior()
        saves = dict(target_source.saving_throw_bonuses)
        saves["constitution"] = 0
        target = build_combatant_state(target_source.model_copy(update={
            "armor_class": 10, "max_hp": 40, "saving_throw_bonuses": saves,
        }, deep=True))
        effect = OnHitConditionSave(
            save_ability="constitution", dc=12, condition_id="poisoned",
            duration_rounds=10,
            failure_margin_escalation=FailureMarginEscalation(
                margin=5, additional_condition_ids=["unconscious"],
                replacement_duration_dice_count=1,
                replacement_duration_dice_size=10,
                replacement_duration_round_multiplier=10,
                ends_on_damage=True,
                allowed_removal_action_ids=["wake-sleeper"],
            ),
        )
        base_attack = attacker.template.weapon_attack
        attack = base_attack.model_copy(update={
            "id": "synthetic-failure-margin",
            "weapon": base_attack.weapon.model_copy(update={"name": name}),
            "on_hit_condition_save": effect,
        }, deep=True)
        values = [15, 4, 4, save_roll]
        if duration_die is not None:
            values.append(duration_die)
        event = resolve_attack(
            1, 1, attacker, target, attack, 5,
            FixedDiceProvider(values), spend_action=False,
        )
        return event, target
    except Exception:
        raise


def test_failure_by_five_escalates_with_one_shared_duration_and_separate_wake_group():
    event, target = _strike(3, duration_die=4)
    assert event.save_succeeded is False
    assert {"poisoned", "unconscious"} <= set(event.applied_condition_ids)
    poisoned = next(x for x in target.timed_effects if x.effect_id == "poisoned")
    sleeping = next(x for x in target.timed_effects if x.effect_id == "unconscious")
    assert poisoned.expires_round == sleeping.expires_round == 41
    assert poisoned.source_effect_id != sleeping.source_effect_id
    assert sleeping.ends_on_damage is True
    assert sleeping.allowed_removal_action_ids == ["wake-sleeper"]
    assert "prone" in target.active_effect_ids
    assert end_damage_sensitive_effects(target) == ["unconscious"]
    assert "poisoned" in target.active_effect_ids
    assert "unconscious" not in target.active_effect_ids


def test_narrow_failure_and_success_do_not_escalate():
    for save_roll, success in [(9, False), (15, True)]:
        event, target = _strike(save_roll)
        assert event.save_succeeded is success
        assert "unconscious" not in event.applied_condition_ids
        assert not any(x.effect_id == "unconscious" for x in target.timed_effects)


def test_renamed_source_does_not_change_escalation_semantics():
    event, target = _strike(3, duration_die=4, name="Completely Renamed Homebrew")
    assert {"poisoned", "unconscious"} <= set(event.applied_condition_ids)
    assert any(x.source_effect_id == "Completely Renamed Homebrew:escalated" for x in target.timed_effects)


def test_incomplete_replacement_duration_is_rejected_by_card_schema():
    with pytest.raises(ValueError):
        FailureMarginEscalation(
            margin=5, additional_condition_ids=["unconscious"],
            replacement_duration_dice_count=1,
        )
