from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.character_resource_rules import expected_resources
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile

logger = logging.getLogger(__name__)


def build_rowan_2024_combat_profile(level: int = 1) -> PregenCombatProfile:
    try:
        profile = build_rowan_ashtrail_2024_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        resources = tuple(expected_resources(profile).items())
        return PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Ranger",
            level=level,
            abilities=scores,
            save_proficiencies=("strength", "dexterity"),
            armor_class=12 + dexterity,
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=35,
            initiative_bonus=dexterity + pb,
            skill_bonuses=(
                ("athletics", scores.modifier("strength") + pb),
                ("survival", wisdom + pb),
                ("perception", wisdom + pb),
                ("stealth", dexterity + pb),
                ("insight", wisdom + pb),
                ("investigation", scores.modifier("intelligence") + pb),
            ),
            attacks=(
                AttackExpectation(
                    "longbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=150, long_range_ft=600,
                    mastery_property="Slow",
                ),
                AttackExpectation(
                    "shortsword", "dexterity", 1, 6, "piercing",
                    mastery_property="Vex",
                ),
                AttackExpectation(
                    "scimitar", "dexterity", 1, 6, "slashing",
                    mastery_property="Nick",
                ),
            ),
            weapon_masteries=("longbow", "shortsword"),
            resources=resources,
        )
    except Exception:
        logger.exception("Failed to compile Rowan's 2024 combat fingerprint at level %s.", level)
        raise


def build_rowan_2024_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_rowan_2024_combat_profile(1)]
    except Exception:
        logger.exception("Failed to compile Rowan's 2024 combat fingerprint registry.")
        raise
