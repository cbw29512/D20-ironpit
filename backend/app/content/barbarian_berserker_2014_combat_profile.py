from __future__ import annotations

import logging

from app.content.barbarian_berserker_2014_profile import build_rokhan_stonefury_2014_profile
from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.level_resources import barbarian_2014_rage_damage_bonus, barbarian_2014_rage_uses
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def build_rokhan_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        source = build_rokhan_stonefury_2014_profile(level)
        scores = source.final_ability_scores
        pb = proficiency_bonus(level)
        attacks = (
            AttackExpectation("greataxe", "strength", 1, 12, "slashing"),
            AttackExpectation("handaxe", "strength", 1, 6, "slashing", normal_range_ft=20, long_range_ft=60),
        )
        return PregenCombatProfile(
            template_id=source.template_id,
            archetype="Barbarian",
            level=level,
            abilities=scores,
            save_proficiencies=("strength", "constitution"),
            armor_class=10 + scores.modifier("dexterity") + scores.modifier("constitution"),
            max_hp=fixed_hit_points(level, 12, scores.modifier("constitution")),
            speed_ft=40 if level >= 5 else 30,
            skill_bonuses=(
                ("athletics", scores.modifier("strength") + pb),
                ("intimidation", scores.modifier("charisma") + pb),
                ("perception", scores.modifier("wisdom") + pb),
                ("survival", scores.modifier("wisdom") + pb),
            ),
            attacks=attacks,
            weapon_masteries=(),
            resources=(("rage", barbarian_2014_rage_uses(level)), ("relentless-endurance", 1)),
            rage_damage_bonus=barbarian_2014_rage_damage_bonus(level),
            initiative_bonus=scores.modifier("dexterity"),
        )
    except Exception:
        logger.exception("Failed to build 2014 Rokhan combat profile at level %s", level)
        raise


def build_rokhan_2014_combat_profiles() -> list[PregenCombatProfile]:
    return [build_rokhan_2014_combat_profile(level) for level in range(1, 11)]
