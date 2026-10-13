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


def test_stone_giant_2014_binds_source_rock_catching() -> None:
    from app.content.monster_source_2014 import load_monster_source_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.content.capability_compiler import compile_combatant
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014

    source = next(m for m in load_monster_source_2014() if m.id == "stone-giant")
    assert "Rock Catching" in source.reaction_names
    assert "source:reaction" not in basic_blockers_2014(source)
    definition = adapt_basic_monster_2014(source)
    rule = compile_combatant(definition).attack_damage_reduction_reaction
    assert rule is not None
    assert rule.source_name == "Rock Catching"
    assert rule.attack_kinds == ["ranged"]
    assert rule.negate_on_save_ability == "dexterity"
    assert rule.negate_on_save_dc == 10
    assert rule.required_attack_name_tokens


def test_rock_catching_rejects_unrelated_projectiles() -> None:
    from app.combat.attack_damage_reduction import can_reduce_attack_damage
    defender = _defender()
    rule = defender.template.attack_damage_reduction_reaction.model_copy(update={
        "attack_kinds": ["ranged"],
        "required_attack_name_tokens": ["rock", "stone", "boulder"],
    })
    defender.template = defender.template.model_copy(update={
        "attack_damage_reduction_reaction": rule,
    })
    attack = defender.template.weapon_attack.model_copy(update={
        "weapon": defender.template.weapon_attack.weapon.model_copy(update={
            "name": "Longbow", "attack_kind": "ranged",
        }),
    })
    assert can_reduce_attack_damage(defender, attack, _damage()) is False
