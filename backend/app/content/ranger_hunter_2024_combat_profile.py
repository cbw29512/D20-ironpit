from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.character_resource_rules import expected_resources
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.content.ranger_hunter_2024_runtime_support import ranger_2024_skill_bonuses

logger = logging.getLogger(__name__)


def build_rowan_2024_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Rowan combat fingerprint currently covers levels 1 through 20.")
        profile = build_rowan_ashtrail_2024_profile(level)
        scores = profile.final_ability_scores
        dexterity = scores.modifier("dexterity")
        pb = proficiency_bonus(level)
        speed = 45 if level >= 6 else 35
        return PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Ranger",
            level=level,
            abilities=scores,
            save_proficiencies=("strength", "dexterity"),
            armor_class=12 + dexterity,
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=speed,
            initiative_bonus=dexterity + pb,
            skill_bonuses=tuple(ranger_2024_skill_bonuses(scores, level).items()),
            attacks=(
                AttackExpectation(
                    "longbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=150, long_range_ft=600,
                    mastery_property="Slow",
                    style_attack_bonus=2 if level >= 2 else 0,
                ),
                AttackExpectation("shortsword", "dexterity", 1, 6, "piercing", mastery_property="Vex"),
                AttackExpectation("scimitar", "dexterity", 1, 6, "slashing"),
            ),
            weapon_masteries=("longbow", "shortsword"),
            resources=tuple(expected_resources(profile).items()),
            fighting_style="Archery" if level >= 2 else None,
        )
    except Exception:
        logger.exception("Failed to compile Rowan's 2024 combat fingerprint at level %s.", level)
        raise


def build_rowan_2024_combat_profiles() -> list[PregenCombatProfile]:
    return [build_rowan_2024_combat_profile(level) for level in range(1, 21)]
