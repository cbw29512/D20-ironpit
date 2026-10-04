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
        archery_bonus = 2 if "Archery" in profile.fighting_styles else 0
        perception_bonus = wisdom + (2 * pb if level >= 2 else pb)
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
                ("acrobatics", dexterity),
                ("survival", wisdom + pb),
                ("perception", perception_bonus),
                ("stealth", dexterity + pb),
                ("insight", wisdom + pb),
                ("investigation", scores.modifier("intelligence") + pb),
            ),
            attacks=(
                AttackExpectation(
                    "longbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=150, long_range_ft=600,
                    style_attack_bonus=archery_bonus,
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
            fighting_style=profile.fighting_style,
        )
    except Exception:
        logger.exception("Failed to compile Rowan's 2024 combat fingerprint at level %s.", level)
        raise


def build_rowan_2024_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_rowan_2024_combat_profile(level) for level in range(1, 3)]
    except Exception:
        logger.exception("Failed to compile Rowan's 2024 combat fingerprint registry.")
        raise
