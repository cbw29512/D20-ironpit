from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def build_thalen_2024_combat_profiles() -> tuple[PregenCombatProfile, ...]:
    """Independent source-derived fingerprint for certified 2024 Druid levels."""
    try:
        abilities = AbilityScores(
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=13,
            wisdom=17,
            charisma=15,
        )
        return (
            PregenCombatProfile(
                template_id="thalen-greenbough-l1",
                archetype="Druid",
                level=1,
                abilities=abilities,
                save_proficiencies=("intelligence", "wisdom"),
                armor_class=13,
                max_hp=8,
                speed_ft=35,
                skill_bonuses=(
                    ("athletics", 0),
                    ("acrobatics", 0),
                    ("nature", 6),
                    ("survival", 5),
                    ("insight", 5),
                    ("religion", 3),
                    ("perception", 5),
                ),
                attacks=(
                    AttackExpectation(
                        "sickle", "strength", 1, 4, "slashing",
                    ),
                ),
                weapon_masteries=(),
                resources=(("spell-slot-1", 2),),
                initiative_bonus=0,
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Thalen combat fingerprint.")
        raise
