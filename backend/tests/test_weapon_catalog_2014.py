import pytest

from app.content.weapon_catalog_2014 import (
    build_weapon_2014,
    official_weapon_ids_2014,
    select_damage_mode_2014,
)
from app.domain.models import DamageType, WeaponAttackKind


def test_2014_catalog_contains_all_basic_rules_weapons() -> None:
    assert len(official_weapon_ids_2014()) == 37
    assert len(set(official_weapon_ids_2014())) == 37


def test_quarterstaff_uses_highest_legal_damage_mode() -> None:
    quarterstaff = build_weapon_2014("quarterstaff")
    assert quarterstaff.damage_type == DamageType.BLUDGEONING
    assert quarterstaff.properties == ("versatile",)
    assert select_damage_mode_2014("quarterstaff", second_hand_free=True) == (1, 8, None)
    assert select_damage_mode_2014("quarterstaff", second_hand_free=False) == (1, 6, None)


def test_spear_matches_2014_rules() -> None:
    spear = build_weapon_2014("spear")
    assert spear.attack_kind == WeaponAttackKind.MELEE
    assert spear.damage_type == DamageType.PIERCING
    assert (spear.dice_count, spear.dice_size) == (1, 6)
    assert (spear.normal_range_ft, spear.long_range_ft) == (20, 60)
    assert (spear.versatile_dice_count, spear.versatile_dice_size) == (1, 8)


def test_two_handed_weapon_is_illegal_without_second_hand() -> None:
    with pytest.raises(ValueError, match="requires two hands"):
        select_damage_mode_2014("greatsword", second_hand_free=False)


def test_fixed_and_non_damage_weapons_are_preserved() -> None:
    blowgun = build_weapon_2014("blowgun")
    net = build_weapon_2014("net")
    assert (blowgun.dice_count, blowgun.dice_size, blowgun.fixed_damage) == (0, None, 1)
    assert (net.dice_count, net.dice_size, net.fixed_damage, net.damage_type) == (0, None, None, None)


def test_catalog_returns_independent_records() -> None:
    first = build_weapon_2014("quarterstaff")
    second = build_weapon_2014("quarterstaff")
    first.name = "Changed"
    assert second.name == "Quarterstaff"


def test_unknown_2014_weapon_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown 2014 weapon"):
        build_weapon_2014("not-a-weapon")
