import pytest

from app.content.canonical_spell_packages import build_class_spell_package, build_level_one_package
from app.content.class_spell_progression import max_spell_level, mystic_arcanum_levels, prepared_spell_count
from app.content.melee_loadout_policy import choose_melee_loadout


def test_full_caster_prepared_counts_follow_2024_tables() -> None:
    assert prepared_spell_count("wizard", 1) == 4
    assert prepared_spell_count("wizard", 5) == 9
    assert prepared_spell_count("wizard", 20) == 25
    assert prepared_spell_count("cleric", 1) == 4
    assert prepared_spell_count("cleric", 20) == 22
    assert prepared_spell_count("sorcerer", 1) == 2
    assert prepared_spell_count("sorcerer", 20) == 22


def test_half_caster_and_warlock_progressions_are_distinct() -> None:
    assert prepared_spell_count("paladin", 5) == 6
    assert prepared_spell_count("ranger", 17) == 14
    assert prepared_spell_count("warlock", 1) == 2
    assert prepared_spell_count("warlock", 11) == 11
    assert prepared_spell_count("warlock", 20) == 15
    assert max_spell_level("paladin", 5) == 2
    assert max_spell_level("wizard", 5) == 3
    assert max_spell_level("warlock", 9) == 5
    assert mystic_arcanum_levels(17) == (6, 7, 8, 9)


def test_level_one_spell_packages_are_shared_by_class() -> None:
    wizard = build_level_one_package("wizard")
    assert [spell.name for spell in wizard.spells] == [
        "Mage Armor", "Magic Missile", "Sleep", "Thunderwave",
    ]
    cleric = build_level_one_package("cleric")
    assert [spell.name for spell in cleric.spells] == [
        "Bless", "Cure Wounds", "Guiding Bolt", "Shield of Faith",
    ]
    assert build_level_one_package("warlock").casting_ability == "charisma"
    assert build_level_one_package("druid").casting_ability == "wisdom"


def test_higher_level_spell_package_fails_closed_until_filled() -> None:
    with pytest.raises(ValueError, match="canonical package is incomplete"):
        build_class_spell_package("wizard", 2)


def test_melee_policy_is_repeatable_from_physical_build() -> None:
    assert choose_melee_loadout(10, 16, shield_trained=True).kind == "dual-wield"
    assert choose_melee_loadout(16, 10, shield_trained=True).kind == "one-hander-shield"
    assert choose_melee_loadout(16, 10, shield_trained=True, power_build=True).kind == "two-handed"
    assert choose_melee_loadout(16, 10, shield_trained=False).kind == "two-handed"
