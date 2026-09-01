from __future__ import annotations

import pytest

from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.audited_cleric_profile import build_seraphine_dawnshield_profile
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.canonical_combat_build_policy import (
    CANONICAL_POINT_BUY_ARRAY,
    CANONICAL_STAT_PRIORITIES,
    assert_canonical_base_array,
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import AbilityScores


def test_every_canonical_class_has_one_mass_production_stat_policy() -> None:
    assert set(CANONICAL_STAT_PRIORITIES) == set(HERO_BY_CLASS)


def test_canonical_base_array_is_always_legal_15_14_13_10_10_10() -> None:
    for class_id in HERO_BY_CLASS:
        scores = canonical_base_ability_scores(class_id)
        assert tuple(sorted(scores.model_dump().values(), reverse=True)) == CANONICAL_POINT_BUY_ARRAY


def test_weapon_first_builds_dump_all_three_mental_scores_to_ten() -> None:
    for class_id in ("barbarian", "fighter", "monk", "paladin", "ranger", "rogue"):
        scores = canonical_base_ability_scores(class_id)
        assert (scores.intelligence, scores.wisdom, scores.charisma) == (10, 10, 10)


def test_primary_casters_dump_all_three_physical_scores_to_ten() -> None:
    for class_id in ("bard", "cleric", "druid", "sorcerer", "warlock", "wizard"):
        scores = canonical_base_ability_scores(class_id)
        assert (scores.strength, scores.dexterity, scores.constitution) == (10, 10, 10)


def test_representative_primary_and_secondary_priorities() -> None:
    assert canonical_base_ability_scores("barbarian") == AbilityScores(
        strength=15, constitution=14, dexterity=13, intelligence=10, wisdom=10, charisma=10,
    )
    assert canonical_base_ability_scores("ranger") == AbilityScores(
        dexterity=15, constitution=14, strength=13, intelligence=10, wisdom=10, charisma=10,
    )
    assert canonical_base_ability_scores("cleric") == AbilityScores(
        wisdom=15, charisma=14, intelligence=13, strength=10, dexterity=10, constitution=10,
    )


def test_background_increases_follow_primary_then_next_allowed_priority() -> None:
    fighter = canonical_background_increases("fighter", ["strength", "dexterity", "constitution"])
    assert [(item.ability, item.amount) for item in fighter] == [("strength", 2), ("constitution", 1)]

    cleric = canonical_background_increases("cleric", ["constitution", "intelligence", "wisdom"])
    assert [(item.ability, item.amount) for item in cleric] == [("wisdom", 2), ("intelligence", 1)]


def test_existing_canonical_roots_are_migrated_to_the_mass_production_policy() -> None:
    for profile in (
        build_karnok_stoneward_profile(),
        build_rokhan_stonefury_profile(),
        build_seraphine_dawnshield_profile(),
    ):
        assert_canonical_profile_policy(profile)
        assert profile.base_ability_scores == canonical_base_ability_scores(profile.class_id)


def test_background_policy_fails_closed_when_primary_is_not_legal() -> None:
    with pytest.raises(ValueError, match="must allow its primary"):
        canonical_background_increases("wizard", ["strength", "dexterity", "constitution"])


def test_explicit_base_array_validator_rejects_old_standard_array_shape() -> None:
    old_fighter = AbilityScores(
        strength=15, dexterity=13, constitution=14, intelligence=8, wisdom=12, charisma=10,
    )
    with pytest.raises(ValueError, match="canonical base abilities drifted"):
        assert_canonical_base_array("fighter", old_fighter)
