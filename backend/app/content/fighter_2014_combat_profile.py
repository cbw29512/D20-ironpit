from __future__ import annotations

import logging
import math

from app.content.fighter_2014 import karnok_2014_template_id
from app.content.fighter_2014_combat_levels import fighter_2014_level
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def _modifier(score: int) -> int:
    return (score - 10) // 2


def build_karnok_stoneward_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        row = fighter_2014_level(level)
        abilities = AbilityScores(
            strength=row.strength,
            dexterity=row.dexterity,
            constitution=row.constitution,
            intelligence=row.intelligence,
            wisdom=row.wisdom,
            charisma=row.charisma,
        )
        half_pb = math.ceil(row.proficiency_bonus / 2) if row.remarkable_athlete else 0
        resources: list[tuple[str, int]] = [("second-wind", row.second_wind_uses)]
        if row.action_surge_uses:
            resources.append(("action-surge", row.action_surge_uses))
        if row.indomitable_uses:
            resources.append(("indomitable", row.indomitable_uses))
        attacks = (
            AttackExpectation("greatsword", "strength", 2, 6, "slashing"),
            AttackExpectation(
                "longbow", "dexterity", 1, 8, "piercing",
                normal_range_ft=150, long_range_ft=600,
                style_attack_bonus=2 if "Archery" in row.fighting_styles else 0,
            ),
        )
        return PregenCombatProfile(
            template_id=karnok_2014_template_id(level),
            archetype="Fighter",
            level=level,
            abilities=abilities,
            save_proficiencies=("strength", "constitution"),
            armor_class=17,
            max_hp=row.max_hp,
            speed_ft=30,
            skill_bonuses=(
                ("athletics", row.proficiency_bonus + _modifier(row.strength)),
                ("acrobatics", _modifier(row.dexterity) + half_pb),
                ("intimidation", row.proficiency_bonus + _modifier(row.charisma)),
                ("perception", row.proficiency_bonus + _modifier(row.wisdom)),
            ),
            attacks=attacks,
            weapon_masteries=(),
            resources=tuple(resources),
            fighting_style="Defense",
            initiative_bonus=_modifier(row.dexterity) + half_pb,
        )
    except Exception:
        logger.exception("Failed to build 2014 Karnok combat fingerprint level %s.", level)
        raise


def build_karnok_stoneward_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_karnok_stoneward_2014_combat_profile(level) for level in range(1, 11)]
    except Exception:
        logger.exception("Failed to build the 2014 Karnok combat fingerprint progression.")
        raise
