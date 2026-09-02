from app.content.subclass_specializations import FIGHTER_SPECIALIZATIONS, subclass_specialization
from app.content.weapon_catalog import build_weapon


def test_fighter_has_one_coherent_specialization_per_subclass() -> None:
    by_subclass = {item.subclass_id: item for item in FIGHTER_SPECIALIZATIONS}
    assert set(by_subclass) == {"champion", "battle-master", "eldritch-knight", "psi-warrior"}
    assert by_subclass["champion"].role == "two-handed"
    assert by_subclass["battle-master"].role == "dual-wield"
    assert by_subclass["eldritch-knight"].role == "sword-shield"
    assert by_subclass["psi-warrior"].role == "ranged"


def test_weapon_specializations_are_only_catalog_data_and_mastery_choices() -> None:
    for spec in FIGHTER_SPECIALIZATIONS:
        assert spec.primary_weapon is not None
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
