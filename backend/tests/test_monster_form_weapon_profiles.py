from __future__ import annotations

import pytest

from app.combat.monster_form_weapon_profiles import (
    SourceAttackAbility, compose_monster_form_weapon_profiles,
)
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.domain.character_builds import AbilityScores
from app.domain.weapons import OnHitDamage, DamageType
from app.domain.damage_sources import DamageSourceQualifier


def _pair():
    wolf = canonical_wild_shape_template_2014(2)
    mace = wolf.weapon_attack.model_copy(update={
        "id": "angel-mace", "attack_bonus": 8, "damage_bonus": 4,
        "attack_ability": "strength", "attack_ability_modifier": 4,
        "on_hit_damage": [OnHitDamage(
            source="printed-radiant-rider", dice_count=4, dice_size=8,
            damage_type=DamageType.RADIANT,
        )],
        "damage_source_qualifiers": [DamageSourceQualifier.MAGICAL],
    }, deep=True)
    owner = wolf.model_copy(update={
        "id": "2014-original-monster", "kind": "monster",
        "challenge_rating": "10", "weapon_attack": mace, "alternate_weapon_attacks": [],
        "ability_scores": AbilityScores(
            strength=18, dexterity=18, constitution=18,
            intelligence=17, wisdom=20, charisma=20,
        ),
    }, deep=True)
    form = wolf.model_copy(update={
        "id": "2014-source-form", "kind": "monster",
        "challenge_rating": "1/4",
        "ability_scores": wolf.ability_scores.model_copy(update={"strength": 12}),
    }, deep=True)
    return owner, form


def test_retained_attack_rebases_without_redoubling_printed_rider() -> None:
    owner, form = _pair()
    result = compose_monster_form_weapon_profiles(owner, form, owner_attack_abilities={
        "angel-mace": SourceAttackAbility("strength", True),
    })
    retained, gained = result
    assert retained.id == "angel-mace"
    assert retained.attack_bonus == 5 and retained.damage_bonus == 1
    assert retained.attack_ability_modifier == 1
    assert retained.on_hit_damage == owner.weapon_attack.on_hit_damage
    assert len(retained.on_hit_damage) == 1
    assert retained.on_hit_damage[0].dice_count == 4
    assert retained.damage_source_qualifiers == [DamageSourceQualifier.MAGICAL]
    assert gained == form.weapon_attack
    assert gained is not form.weapon_attack
    assert owner.weapon_attack.attack_bonus == 8 and owner.weapon_attack.damage_bonus == 4


def test_fail_closed_when_printed_attack_ability_or_damage_provenance_missing() -> None:
    owner, form = _pair()
    with pytest.raises(ValueError, match="provenance"):
        compose_monster_form_weapon_profiles(owner, form, owner_attack_abilities={})
    with pytest.raises(ValueError, match="conflicts"):
        compose_monster_form_weapon_profiles(owner, form, owner_attack_abilities={
            "angel-mace": SourceAttackAbility("dexterity", True),
        })
    with pytest.raises(ValueError, match="same-edition"):
        compose_monster_form_weapon_profiles(owner, form.model_copy(update={"ruleset": "2024"}),
            owner_attack_abilities={"angel-mace": SourceAttackAbility("strength", True)})
    with pytest.raises(ValueError, match="Fixed-damage"):
        fixed = owner.weapon_attack.model_copy(update={"fixed_damage": 7})
        compose_monster_form_weapon_profiles(owner.model_copy(update={"weapon_attack": fixed}), form,
            owner_attack_abilities={"angel-mace": SourceAttackAbility("strength", True)})


def test_static_bonus_and_original_rider_survive_form_merge() -> None:
    owner, form = _pair()
    constant = owner.weapon_attack.model_copy(update={
        "attack_ability": None, "attack_ability_modifier": None,
        "attack_bonus": 7, "damage_bonus": 0,
    })
    owner = owner.model_copy(update={"weapon_attack": constant})
    original = compose_monster_form_weapon_profiles(owner, form, owner_attack_abilities={
        "angel-mace": SourceAttackAbility("fixed", False),
    })
    assert original[0].attack_bonus == 7
    assert original[0].damage_bonus == 0
    assert original[0].on_hit_damage[0].dice_count == 4
