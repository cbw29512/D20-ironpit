from app.combat.dice import FixedDiceProvider
from app.combat.on_hit_saves import resolve_on_hit_save
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.demo import build_demo_fighter
from app.domain.on_hit_saves import OnHitSaveEffect
from app.domain.weapons import Weapon, WeaponAttack, WeaponAttackKind


def _attack(effect: OnHitSaveEffect) -> WeaponAttack:
    return WeaponAttack(
        id="test-bite",
        weapon=Weapon(
            id="test-bite", name="Bite", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=6, damage_type="piercing", animation="melee",
        ),
        attack_bonus=5, damage_bonus=3, on_hit_save_effect=effect,
    )


def _prone_bite() -> WeaponAttack:
    return _attack(OnHitSaveEffect(save_ability="strength", dc=20, condition_id="prone"))


def test_on_hit_save_condition_applies_only_on_failed_save() -> None:
    failed = build_combatant_state(build_demo_fighter())
    failure = resolve_on_hit_save(failed, _prone_bite(), FixedDiceProvider([1]))
    assert failure.save_succeeded is False
    assert failure.applied_condition == "prone"
    assert "prone" in failed.active_effect_ids

    succeeded = build_combatant_state(build_demo_fighter())
    success = resolve_on_hit_save(succeeded, _prone_bite(), FixedDiceProvider([20]))
    assert success.save_succeeded is True
    assert success.applied_condition is None
    assert "prone" not in succeeded.active_effect_ids


def test_timed_poison_preserves_printed_end_of_turn_repeat_save() -> None:
    target = build_combatant_state(build_demo_fighter())
    attack = _attack(OnHitSaveEffect(
        save_ability="constitution", dc=14, condition_id="poisoned",
        duration_rounds=10, repeat_save_timing="target_turn_end",
    ))
    result = resolve_on_hit_save(
        target, attack, FixedDiceProvider([1]), source_id="venomous-monster", round_number=3,
    )
    assert result.save_succeeded is False
    assert result.applied_condition == "poisoned"
    assert len(target.timed_effects) == 1
    effect = target.timed_effects[0]
    assert effect.source_id == "venomous-monster"
    assert effect.source_effect_id == "test-bite"
    assert effect.applied_round == 3
    assert effect.expires_round == 13
    assert effect.repeat_save_ability == "constitution"
    assert effect.repeat_save_dc == 14
    assert effect.repeat_save_timing == "target_turn_end"


def test_poison_default_does_not_override_explicit_repeat_timing() -> None:
    target = build_combatant_state(build_demo_fighter())
    apply_timed_condition(
        target, "poisoned", "source", applied_round=1, expires_round=11,
        repeat_save_ability="constitution", repeat_save_dc=12,
        repeat_save_timing="target_turn_end",
    )
    assert target.timed_effects[0].repeat_save_timing == "target_turn_end"
