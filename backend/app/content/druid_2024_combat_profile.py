from __future__ import annotations

import logging

from app.content.druid_2024_combat_profile_high import build_thalen_2024_high_combat_profiles
from app.content.druid_2024_combat_profile_low import build_thalen_2024_low_combat_profiles
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
        abilities_l4 = abilities.model_copy(update={"wisdom": 19})
        abilities_l8 = abilities_l4.model_copy(update={"wisdom": 20, "charisma": 16})
        attacks = (AttackExpectation("sickle", "strength", 1, 4, "slashing"),)
        return (
            *build_thalen_2024_low_combat_profiles(
                abilities,
                abilities_l4,
                abilities_l8,
                attacks,
            ),
            *build_thalen_2024_high_combat_profiles(abilities_l8, attacks),
        )
    except Exception:
        logger.exception("Failed to build 2024 Thalen combat fingerprint.")
        raise
