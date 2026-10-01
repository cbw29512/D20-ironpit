from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def build_kael_2024_combat_profiles(max_level: int = 1) -> list[PregenCombatProfile]:
    """Return the certified 2024 Kael combat fingerprint for implemented levels."""
    try:
        if max_level != 1:
            raise ValueError("The current 2024 Kael combat fingerprint covers level 1 only.")
        abilities = AbilityScores(
            strength=13,
            dexterity=17,
            constitution=15,
            intelligence=10,
            wisdom=10,
            charisma=10,
        )
        return [
            PregenCombatProfile(
                template_id="kael-stillwater-l1",
                archetype="Monk",
                level=1,
                abilities=abilities,
                save_proficiencies=("strength", "dexterity"),
                armor_class=13,
                max_hp=10,
                speed_ft=30,
                initiative_bonus=5,
                skill_bonuses=(
                    ("athletics", 1),
                    ("acrobatics", 5),
                    ("history", 2),
                    ("insight", 2),
                    ("nature", 2),
                    ("perception", 2),
                    ("religion", 2),
                    ("sleight-of-hand", 5),
                    ("stealth", 5),
                ),
                attacks=(
                    AttackExpectation(
                        "unarmed-strike",
                        "dexterity",
                        1,
                        6,
                        "bludgeoning",
                    ),
                ),
                weapon_masteries=(),
                resources=(),
            ),
        ]
    except Exception:
        logger.exception("Failed to build 2024 Kael combat fingerprint through level %s.", max_level)
        raise
