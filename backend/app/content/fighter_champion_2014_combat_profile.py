from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.fighter_champion_2014_profile import build_karnok_stoneward_2014_profile
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def _remarkable_athlete_bonus(level: int) -> int:
    return (proficiency_bonus(level) + 1) // 2 if level >= 7 else 0


def build_karnok_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        source = build_karnok_stoneward_2014_profile(level)
        scores = source.final_ability_scores
        pb = proficiency_bonus(level)
        remarkable = _remarkable_athlete_bonus(level)
        resources = [("second-wind", 1)]
        if level >= 2:
            resources.append(("action-surge", 1))
        if level >= 9:
            resources.append(("indomitable", 1))
        attacks = (
            AttackExpectation("greatsword", "strength", 2, 6, "slashing"),
            AttackExpectation(
                "longbow", "dexterity", 1, 8, "piercing",
                normal_range_ft=150, long_range_ft=600,
                style_attack_bonus=2 if level >= 10 else 0,
            ),
        )
        return PregenCombatProfile(
            template_id=source.template_id,
            archetype="Fighter",
            level=level,
            abilities=scores,
            save_proficiencies=("strength", "constitution"),
            armor_class=17,
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("athletics", scores.modifier("strength") + pb),
                ("acrobatics", scores.modifier("dexterity") + remarkable),
            ),
            attacks=attacks,
            weapon_masteries=(),
            resources=tuple(resources),
            fighting_style="Defense",
            initiative_bonus=scores.modifier("dexterity") + remarkable,
        )
    except Exception:
        logger.exception("Failed to build 2014 Karnok combat profile at level %s", level)
        raise


def build_karnok_2014_combat_profiles() -> list[PregenCombatProfile]:
    return [build_karnok_2014_combat_profile(level) for level in range(1, 11)]
