from app.combat.dice import FixedDiceProvider
from app.combat.on_hit_saves import resolve_on_hit_save
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.on_hit_saves import OnHitSaveEffect, SaveFailureMarginEscalation
from app.domain.weapons import Weapon, WeaponAttack, WeaponAttackKind


def _attack(effect: OnHitSaveEffect) -> WeaponAttack:
    return WeaponAttack(
        id="margin-bite",
        weapon=Weapon(id="margin-bite", name="Bite", attack_kind=WeaponAttackKind.MELEE,
                      dice_count=1, dice_size=4, damage_type="piercing", animation="melee"),
        attack_bonus=4, damage_bonus=0, on_hit_save_effect=effect,
    )


def _bite() -> WeaponAttack:
    return _attack(OnHitSaveEffect(
        save_ability="constitution", dc=10, condition_id="poisoned", duration_rounds=10,
        failure_margin_escalation=SaveFailureMarginEscalation(
            margin=5, additional_condition_ids=["unconscious"],
            replacement_duration_dice_count=1, replacement_duration_dice_size=10,
            replacement_duration_round_multiplier=10,
        ),
    ))


def _sleep_poison() -> WeaponAttack:
    return _attack(OnHitSaveEffect(
        save_ability="constitution", dc=10, condition_id="poisoned", duration_rounds=10,
        failure_margin_escalation=SaveFailureMarginEscalation(
            margin=5, additional_condition_ids=["unconscious"], ends_on_damage=True,
            allowed_removal_action_ids=["wake-sleeper"],
        ),
    ))


def _target():
    target = build_combatant_state(build_demo_fighter())
    target.template.saving_throw_bonuses["constitution"] = 0
    return target


def test_failure_by_less_than_margin_keeps_primary_condition_duration() -> None:
    target = _target()
    result = resolve_on_hit_save(target, _bite(), FixedDiceProvider([6]), source_id="source", round_number=2)
    assert result.save_succeeded is False
    assert result.applied_conditions == ["poisoned"]
    assert target.active_effect_ids.count("poisoned") == 1
    assert "unconscious" not in target.active_effect_ids
    assert target.timed_effects[0].expires_round == 12


def test_failure_by_margin_adds_condition_and_rolls_replacement_duration() -> None:
    target = _target()
    result = resolve_on_hit_save(target, _bite(), FixedDiceProvider([5, 7]), source_id="source", round_number=2)
    assert result.save_succeeded is False
    assert set(result.applied_conditions) == {"poisoned", "unconscious"}
    assert {item.effect_id for item in target.timed_effects} == {"poisoned", "unconscious"}
    assert {item.expires_round for item in target.timed_effects} == {72}


def test_sleep_escalation_has_independent_wake_lifecycle() -> None:
    target = _target()
    result = resolve_on_hit_save(target, _sleep_poison(), FixedDiceProvider([5]), source_id="source", round_number=2)
    assert set(result.applied_conditions) == {"poisoned", "unconscious"}
    effects = {item.effect_id: item for item in target.timed_effects}
    assert effects["poisoned"].ends_on_damage is False
    assert effects["poisoned"].allowed_removal_action_ids == []
    assert effects["unconscious"].ends_on_damage is True
    assert effects["unconscious"].allowed_removal_action_ids == ["wake-sleeper"]
    assert effects["unconscious"].expires_round == 12
