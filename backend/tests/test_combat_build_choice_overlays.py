from app.content.combat_build_choice_overlays import (
    FIGHTER_COMBAT_BUILD_CHOICES,
    get_combat_build_choice_overlay,
)
from app.content.combat_build_variants import get_combat_build_variant


def test_all_fighter_role_variants_have_choice_overlays() -> None:
    expected = {"great-weapon", "sword-shield", "archer", "dual-wield"}
    assert set(FIGHTER_COMBAT_BUILD_CHOICES) == expected
    assert {get_combat_build_variant("fighter", build_id).id for build_id in expected} == expected


def test_fighter_builds_share_progression_but_make_distinct_role_choices() -> None:
    great = get_combat_build_choice_overlay("fighter", "great-weapon")
    shield = get_combat_build_choice_overlay("fighter", "sword-shield")
    archer = get_combat_build_choice_overlay("fighter", "archer")
    dual = get_combat_build_choice_overlay("fighter", "dual-wield")

    assert (great.primary_ability, great.fighting_style, great.primary_weapon) == (
        "strength", "Great Weapon Fighting", "greatsword",
    )
    assert shield.shield is True and shield.primary_weapon == "longsword"
    assert (archer.primary_ability, archer.fighting_style, archer.primary_weapon) == (
        "dexterity", "Archery", "longbow",
    )
    assert (dual.primary_ability, dual.fighting_style, dual.primary_weapon) == (
        "dexterity", "Two-Weapon Fighting", "shortsword",
    )


def test_dual_wield_fighter_declares_nick_and_vex_as_shared_engine_requirements() -> None:
    dual = get_combat_build_choice_overlay("fighter", "dual-wield")
    assert dual.weapon_masteries[:2] == ("shortsword", "scimitar")
    assert dual.secondary_weapons[0] == "scimitar"
    assert {"nick-mastery", "vex-mastery"} <= set(dual.required_capabilities)


def test_archer_does_not_turn_slow_into_an_arena_engine_requirement() -> None:
    archer = get_combat_build_choice_overlay("fighter", "archer")
    assert "slow-mastery" in archer.arena_ignored
    assert "slow-mastery" not in archer.required_capabilities


def test_sword_and_shield_is_a_real_distinct_defender_overlay() -> None:
    shield = get_combat_build_choice_overlay("fighter", "sword-shield")
    assert shield.armor == "chain-mail"
    assert shield.shield is True
    assert shield.fighting_style == "Defense"
    assert "sap-mastery" in shield.required_capabilities
