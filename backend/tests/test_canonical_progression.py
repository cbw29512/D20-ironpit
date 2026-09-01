import pytest

from app.content.audited_fighter import build_karnok_stoneward
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.canonical_hero_policy import canonical_template_id
from app.content.canonical_progression import advance_profile_data, advance_template_data
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.fighter_progression_profile import (
    build_karnok_stoneward_level2_profile,
    build_karnok_stoneward_level3_profile,
    build_karnok_stoneward_level4_profile,
    build_karnok_stoneward_level5_profile,
)


def test_fighter_runtime_levels_are_one_persistent_combatant() -> None:
    levels = [build_karnok_stoneward_level(level) for level in range(1, 6)]
    for level, template in enumerate(levels, start=1):
        assert template.id == canonical_template_id("fighter", level)
        assert template.name == "Karnok Stoneward"
        assert template.archetype == "Fighter"
        assert template.level == level
        assert template.weapon_attack.weapon.id == "greatsword"
        assert [attack.weapon.id for attack in template.alternate_weapon_attacks] == ["shortbow"]


def test_fighter_profiles_inherit_same_declared_loadout() -> None:
    profiles = [
        build_karnok_stoneward_profile(),
        build_karnok_stoneward_level2_profile(),
        build_karnok_stoneward_level3_profile(),
        build_karnok_stoneward_level4_profile(),
        build_karnok_stoneward_level5_profile(),
    ]
    assert [profile.level for profile in profiles] == [1, 2, 3, 4, 5]
    assert {profile.character_name for profile in profiles} == {"Karnok Stoneward"}
    assert {profile.combat_loadout_kind for profile in profiles} == {"two-handed"}


def test_runtime_progression_rejects_skipped_level() -> None:
    with pytest.raises(ValueError, match="exactly one level"):
        advance_template_data(build_karnok_stoneward(), "fighter", 3)


def test_profile_progression_rejects_skipped_level() -> None:
    with pytest.raises(ValueError, match="exactly one level"):
        advance_profile_data(build_karnok_stoneward_profile(), 3)


def test_runtime_progression_rejects_mutated_previous_identity() -> None:
    previous = build_karnok_stoneward()
    previous.id = "alternate-fighter-l1"
    with pytest.raises(ValueError, match="identity drifted"):
        advance_template_data(previous, "fighter", 2)
