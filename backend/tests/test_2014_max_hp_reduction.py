from app.combat.dice import FixedDiceProvider
from app.combat.hit_points import effective_max_hp
from app.combat.on_hit_saves import resolve_on_hit_save
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.on_hit_saves import OnHitSaveEffect
from app.domain.weapons import Weapon, WeaponAttack, WeaponAttackKind


def _attack(dc: int = 14) -> WeaponAttack:
    return WeaponAttack(
        id="life-drain",
        weapon=Weapon(
            id="life-drain", name="Life Drain", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=8, damage_type="necrotic", animation="melee",
        ),
        attack_bonus=5,
        damage_bonus=3,
        on_hit_save_effect=OnHitSaveEffect(
            save_ability="constitution", dc=dc,
            max_hp_reduction_equals_damage_taken=True, zero_max_hp_kills=True,
        ),
    )


def test_failed_life_drain_save_reduces_max_hp_by_damage_taken() -> None:
    target = build_combatant_state(build_demo_fighter())
    before = effective_max_hp(target)
    result = resolve_on_hit_save(target, _attack(), FixedDiceProvider([1]), triggering_damage_total=7)
    assert result.save_succeeded is False
    assert result.max_hp_reduction == 7
    assert target.max_hp_reduction == 7
    assert effective_max_hp(target) == before - 7


def test_successful_life_drain_save_does_not_reduce_max_hp() -> None:
    target = build_combatant_state(build_demo_fighter())
    before = effective_max_hp(target)
    result = resolve_on_hit_save(target, _attack(), FixedDiceProvider([20]), triggering_damage_total=7)
    assert result.save_succeeded is True
    assert result.max_hp_reduction == 0
    assert effective_max_hp(target) == before


def test_life_drain_kills_when_reduction_reaches_zero_max_hp() -> None:
    target = build_combatant_state(build_demo_fighter())
    amount = effective_max_hp(target)
    result = resolve_on_hit_save(target, _attack(), FixedDiceProvider([1]), triggering_damage_total=amount)
    assert result.max_hp_reduction == amount
    assert effective_max_hp(target) == 0
    assert target.current_hp == 0
    assert target.is_dead and not target.is_alive
