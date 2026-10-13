from __future__ import annotations

from app.combat.attack_damage_reduction import apply_attack_damage_reduction
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.models import DamageRollComponent, DamageType
from app.domain.reactions import AttackDamageReductionReaction


def _defender():
    base = build_kael_stillwater_2024(3)
    rule = AttackDamageReductionReaction(
        source_id="catch-projectile",
        source_name="Catch Projectile",
        attack_kinds=["melee", "ranged"],
        negate_on_save_ability="dexterity",
        negate_on_save_dc=10,
    )
    return build_combatant_state(base.model_copy(update={"attack_damage_reduction_reaction": rule}))


def _damage():
    return [DamageRollComponent(
        source="rock", notation="20", rolls=[], modifier=20,
        damage_type=DamageType.BLUDGEONING, total=20,
    )]


def test_universal_save_negation_success_zeroes_hit_and_spends_reaction():
    defender = _defender()
    hit = defender.template.weapon_attack
    result = apply_attack_damage_reduction(defender, hit, _damage(), FixedDiceProvider([20]))
    assert result.used and result.zeroed_attack
    assert result.components[0].total == 0
    assert result.reduction == 20
    assert defender.reaction_available is False


def test_universal_save_negation_failure_keeps_damage_and_spends_reaction():
    defender = _defender()
    hit = defender.template.weapon_attack
    result = apply_attack_damage_reduction(defender, hit, _damage(), FixedDiceProvider([1]))
    assert result.used and not result.zeroed_attack
    assert result.components[0].total == 20
    assert result.reduction == 0
    assert defender.reaction_available is False


def test_universal_save_negation_cannot_trigger_twice():
    defender = _defender()
    hit = defender.template.weapon_attack
    apply_attack_damage_reduction(defender, hit, _damage(), FixedDiceProvider([20]))
    result = apply_attack_damage_reduction(defender, hit, _damage(), FixedDiceProvider([20]))
    assert not result.used
    assert result.components[0].total == 20


def test_universal_save_negation_success_zeroes_all_damage_components() -> None:
    defender = _defender()
    hit = defender.template.weapon_attack
    damage = [
        DamageRollComponent(
            source="rock", notation="11", rolls=[], modifier=11,
            damage_type=DamageType.BLUDGEONING, total=11,
        ),
        DamageRollComponent(
            source="secondary", notation="7", rolls=[], modifier=7,
            damage_type=DamageType.FIRE, total=7,
        ),
    ]
    result = apply_attack_damage_reduction(defender, hit, damage, FixedDiceProvider([20]))
    assert result.used and result.zeroed_attack
    assert result.reduction == 18
    assert [component.total for component in result.components] == [0, 0]
    assert [component.total for component in damage] == [11, 7]
    assert defender.reaction_available is False


def test_universal_save_negation_failure_preserves_all_damage_components() -> None:
    defender = _defender()
    hit = defender.template.weapon_attack
    damage = [
        DamageRollComponent(
            source="rock", notation="11", rolls=[], modifier=11,
            damage_type=DamageType.BLUDGEONING, total=11,
        ),
        DamageRollComponent(
            source="secondary", notation="7", rolls=[], modifier=7,
            damage_type=DamageType.FIRE, total=7,
        ),
    ]
    result = apply_attack_damage_reduction(defender, hit, damage, FixedDiceProvider([1]))
    assert result.used and not result.zeroed_attack
    assert result.reduction == 0
    assert [component.total for component in result.components] == [11, 7]
    assert defender.reaction_available is False
