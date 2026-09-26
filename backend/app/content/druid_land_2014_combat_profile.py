from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def build_thalen_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level != 1:
            raise ValueError("2014 Thalen combat fingerprint is currently certified only at level 1.")
        abilities = AbilityScores(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=12,
            wisdom=16,
            charisma=10,
        )
        return PregenCombatProfile(
            template_id="thalen-greenbough-2014-l1",
            archetype="Druid",
            level=1,
            abilities=abilities,
            save_proficiencies=("intelligence", "wisdom"),
            armor_class=15,
            max_hp=10,
            speed_ft=35,
            skill_bonuses=(
                ("insight", 5),
                ("religion", 3),
                ("perception", 5),
                ("survival", 5),
            ),
            attacks=(
                AttackExpectation("scimitar", "dexterity", 1, 6, "slashing"),
            ),
            weapon_masteries=(),
            resources=(("spell-slot-1", 2),),
        )
    except Exception:
        logger.exception("Failed to compile Thalen's 2014 combat fingerprint at level %s.", level)
        raise


def build_thalen_2014_combat_profiles() -> list[PregenCombatProfile]:
    return [build_thalen_2014_combat_profile(1)]
