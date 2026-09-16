from __future__ import annotations

import logging

from app.content.fighter_2014 import karnok_2014_template_id
from app.content.fighter_2014_combat_levels import fighter_2014_level
from app.domain.character_builds import AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)

_BASE_SCORES = AbilityScores(
    strength=15,
    dexterity=13,
    constitution=15,
    intelligence=10,
    wisdom=10,
    charisma=8,
)


def assert_karnok_2014_profile_policy(profile: CharacterBuildProfile) -> None:
    """Fail closed if the canonical 2014 Fighter progression drifts from its legal build contract."""
    try:
        row = fighter_2014_level(profile.level)
        if profile.ruleset != "2014":
            raise ValueError("2014 Karnok profile crossed the ruleset boundary.")
        if (profile.character_name, profile.class_id, profile.class_name) != (
            "Karnok Stoneward", "fighter", "Fighter",
        ):
            raise ValueError("2014 Karnok identity drifted.")
        if profile.template_id != karnok_2014_template_id(profile.level):
            raise ValueError("2014 Karnok runtime template identity drifted.")
        if (profile.species_id, profile.background_id) != ("human", "soldier"):
            raise ValueError("2014 Karnok must remain a Human Soldier.")
        if profile.base_ability_scores != _BASE_SCORES:
            raise ValueError("2014 Karnok point-buy array drifted.")
        if profile.final_ability_scores != AbilityScores(
            strength=row.strength,
            dexterity=row.dexterity,
            constitution=row.constitution,
            intelligence=row.intelligence,
            wisdom=row.wisdom,
            charisma=row.charisma,
        ):
            raise ValueError("2014 Karnok final ability scores drifted.")
        expected_subclass = "champion" if profile.level >= 3 else None
        if profile.subclass_id != expected_subclass:
            raise ValueError("2014 Champion subclass timing drifted.")
        if profile.fighting_styles != list(row.fighting_styles):
            raise ValueError("2014 Karnok fighting styles drifted.")
        if profile.weapon_masteries:
            raise ValueError("2014 Karnok cannot contain Weapon Mastery.")
    except Exception:
        logger.exception("2014 Karnok profile policy validation failed at level %s.", profile.level)
        raise
