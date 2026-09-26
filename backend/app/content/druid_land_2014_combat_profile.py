from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def build_thalen_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 10):
            raise ValueError("2014 Thalen combat fingerprint currently covers levels 1 through 9.")
        abilities = AbilityScores(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=12,
            wisdom=20 if level >= 8 else (18 if level >= 4 else 16),
            charisma=10,
        )
        return PregenCombatProfile(
            template_id=f"thalen-greenbough-2014-l{level}",
            archetype="Druid",
            level=level,
            abilities=abilities,
            save_proficiencies=("intelligence", "wisdom"),
            armor_class=15,
            max_hp={1: 10, 2: 17, 3: 24, 4: 31, 5: 38, 6: 45, 7: 52, 8: 59, 9: 66}[level],
            speed_ft=35,
            skill_bonuses=(
                ("insight", 9 if level >= 9 else (8 if level >= 8 else (7 if level >= 5 else (6 if level >= 4 else 5)))),
                ("religion", 5 if level >= 9 else (4 if level >= 5 else 3)),
                ("perception", 9 if level >= 9 else (8 if level >= 8 else (7 if level >= 5 else (6 if level >= 4 else 5)))),
                ("survival", 9 if level >= 9 else (8 if level >= 8 else (7 if level >= 5 else (6 if level >= 4 else 5)))),
            ),
            attacks=(
                AttackExpectation("scimitar", "dexterity", 1, 6, "slashing"),
            ),
            weapon_masteries=(),
            resources={
                1: (("spell-slot-1", 2),),
                2: (("spell-slot-1", 3), ("wild-shape", 2)),
                3: (("spell-slot-1", 4), ("spell-slot-2", 2), ("wild-shape", 2)),
                4: (("spell-slot-1", 4), ("spell-slot-2", 3), ("wild-shape", 2)),
                5: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 2), ("wild-shape", 2)),
                6: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("wild-shape", 2)),
                7: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 1), ("wild-shape", 2)),
                8: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 2), ("wild-shape", 2)),
                9: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 1), ("wild-shape", 2)),
            }[level],
        )
    except Exception:
        logger.exception("Failed to compile Thalen's 2014 combat fingerprint at level %s.", level)
        raise


def build_thalen_2014_combat_profiles() -> list[PregenCombatProfile]:
    return [build_thalen_2014_combat_profile(level) for level in range(1, 10)]
