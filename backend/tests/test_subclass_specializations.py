import pytest

from app.content.subclass_specializations import (
    BARBARIAN_SPECIALIZATIONS,
    FIGHTER_SPECIALIZATIONS,
    MONK_SPECIALIZATIONS,
    SubclassSpecialization,
    specializations_for_class,
    subclass_specialization,
)
from app.content.weapon_catalog import build_weapon


def test_fighter_has_one_coherent_specialization_per_subclass() -> None:
    by_subclass = {item.subclass_id: item for item in FIGHTER_SPECIALIZATIONS}
    assert set(by_subclass) == {"champion", "battle-master", "eldritch-knight", "psi-warrior"}
    assert by_subclass["champion"].role == "two-handed"
    assert by_subclass["battle-master"].role == "dual-wield"
    assert by_subclass["eldritch-knight"].role == "sword-shield"
    assert by_subclass["psi-warrior"].role == "ranged"


def test_weapon_specializations_are_only_catalog_data_and_mastery_choices() -> None:
    for spec in (*FIGHTER_SPECIALIZATIONS, *BARBARIAN_SPECIALIZATIONS):
        assert spec.primary_weapon is not None
        assert spec.source_reference
        weapon = build_weapon(spec.primary_weapon)
        assert weapon.id == spec.primary_weapon
        assert spec.primary_weapon in spec.mastery_priority
        for weapon_id in spec.secondary_weapons:
            assert build_weapon(weapon_id).id == weapon_id


def test_dual_wield_specialization_gets_vex_and_nick_from_weapons_not_subclass_code() -> None:
    spec = subclass_specialization("battle-master")
    assert build_weapon(spec.primary_weapon).mastery_property == "Vex"
    assert build_weapon(spec.secondary_weapons[0]).mastery_property == "Nick"
    assert spec.fighting_style_priority == ("Two-Weapon Fighting",)


def test_eldritch_knight_is_sword_shield_with_spell_package_pointer() -> None:
    spec = subclass_specialization("eldritch-knight")
    assert (spec.primary_weapon, spec.shield, spec.spell_package_id) == (
        "longsword", True, "eldritch-knight",
    )


def test_barbarian_has_one_strength_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("barbarian")) == (
        "path-berserker", "path-wild-heart", "path-zealot",
    )
    berserker, wild_heart, zealot = BARBARIAN_SPECIALIZATIONS
    assert (berserker.role, berserker.primary_weapon) == ("two-handed", "greataxe")
    assert (wild_heart.role, wild_heart.primary_weapon, wild_heart.shield) == (
        "weapon-shield", "battleaxe", True,
    )
    assert (zealot.role, zealot.primary_weapon, zealot.secondary_weapons[0]) == (
        "dual-wield", "shortsword", "scimitar",
    )
    assert all(item.ability_priority[0] == "strength" for item in BARBARIAN_SPECIALIZATIONS)


def test_barbarian_subclass_choices_are_explicit_specialization_data() -> None:
    wild_heart = subclass_specialization("path-wild-heart")
    zealot = subclass_specialization("path-zealot")
    assert wild_heart.feature_choice_ids == (
        "wild-heart-rage-bear", "wild-heart-aspect-elephant-athletics", "wild-heart-power-lion",
    )
    assert zealot.feature_choice_ids == ("zealot-divine-fury-radiant",)


def test_monk_has_one_dexterity_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("monk")) == (
        "warrior-open-hand", "warrior-shadow", "warrior-elements",
    )
    open_hand, shadow, elements = MONK_SPECIALIZATIONS
    assert (open_hand.role, open_hand.primary_weapon) == ("unarmed-offense", None)
    assert (shadow.role, shadow.primary_weapon) == ("weapon-monk", "shortsword")
    assert (elements.role, elements.primary_weapon) == ("defensive-mobile", None)
    assert all(item.ability_priority[:2] == ("dexterity", "wisdom") for item in MONK_SPECIALIZATIONS)
    assert all(not item.mastery_priority for item in MONK_SPECIALIZATIONS)


def test_specialization_without_source_truth_fails_closed() -> None:
    with pytest.raises(ValueError, match="requires a source reference"):
        SubclassSpecialization(
            class_id="barbarian", subclass_id="invalid", subclass_name="Invalid",
            role="two-handed", ability_priority=("strength",), armor=None, shield=False,
            primary_weapon="greataxe", source_reference="",
        )
