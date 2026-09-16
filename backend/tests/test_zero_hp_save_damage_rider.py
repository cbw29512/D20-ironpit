from __future__ import annotations

from app.combat.attack_hit_damage import resolve_attack_hit_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType, RollMode, Weapon
from app.domain.weapons import OnHitSaveDamage, WeaponAttack, WeaponAttackKind
from app.domain.zero_hp_effects import ZeroHpSaveDamageRider


def _attack() -> WeaponAttack:
    return WeaponAttack(
        id="zero-hp-rider-test",
        weapon=Weapon(
            id="test-sting",
            name="Sting",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=4,
            damage_type=DamageType.PIERCING,
            animation="sting",
        ),
        attack_bonus=5,
        damage_bonus=0,
        on_hit_save_damage=OnHitSaveDamage(
            source="Sting poison",
            save_ability="constitution",
            dc=11,
            dice_count=2,
            dice_size=6,
            damage_type=DamageType.POISON,
            success_damage="none",
            zero_hp_rider=ZeroHpSaveDamageRider(
                stable=True,
                condition_ids=["poisoned", "paralyzed"],
                duration_rounds=600,
            ),
        ),
    )


def _target(hp: int):
    source = build_goblin_warrior()
    template = source.model_copy(update={"max_hp": 40}, deep=True)
    state = build_combatant_state(template)
    state.current_hp = hp
    return state


def _resolve(target, dice_values: list[int]):
    attacker = build_combatant_state(build_karnok_stoneward())
    return resolve_attack_hit_damage(
        attacker,
        target,
        _attack(),
        FixedDiceProvider(dice_values),
        critical=False,
        attack_mode=RollMode.NORMAL,
        turn_key="1:giant-wasp",
        bonus_damage=None,
        affected_states=[target],
        sneak_attack_ally_available=False,
    )


def test_save_damage_zero_hp_rider_stabilizes_and_groups_conditions() -> None:
    target = _target(10)
    result = _resolve(target, [4, 1, 6, 6])

    assert result.damage_components[-1].source == "Sting poison"
    assert result.damage_outcome == "unconscious"
    assert target.current_hp == 0
    assert target.is_stable is True
    assert target.is_dead is False
    assert {effect.effect_id for effect in target.timed_effects} >= {"poisoned", "paralyzed"}

    rider_effects = [effect for effect in target.timed_effects if effect.source_effect_id == "Sting poison:zero-hp-save-damage"]
    assert len(rider_effects) == 2
    assert {effect.effect_id for effect in rider_effects} == {"poisoned", "paralyzed"}
    assert {effect.expires_round for effect in rider_effects} == {601}
    assert {effect.expiry_timing for effect in rider_effects} == {"target_turn_start"}
    assert all(effect.repeat_save_ability is None for effect in rider_effects)


def test_rider_does_not_fire_when_weapon_damage_alone_causes_zero_hp() -> None:
    target = _target(4)
    _resolve(target, [4, 1, 6, 6])

    assert target.is_dead is True
    assert target.is_stable is False
    assert not any(
        effect.source_effect_id == "Sting poison:zero-hp-save-damage"
        for effect in target.timed_effects
    )
