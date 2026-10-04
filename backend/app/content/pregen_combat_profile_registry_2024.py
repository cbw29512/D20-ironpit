from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.content.pregen_combat_profiles import PregenCombatProfile

logger = logging.getLogger(__name__)


def build_2024_pregen_combat_profiles() -> list["PregenCombatProfile"]:
    """Collect 2024 class-specific combat fingerprints without growing the core registry."""
    try:
        from app.content.bard_2024_combat_profile import build_lyra_2024_combat_profiles
        from app.content.druid_2024_combat_profile import build_thalen_2024_combat_profiles
        from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
        from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
        from app.content.rogue_combat_fingerprint import build_mara_quickstep_combat_profiles
        from app.content.ranger_hunter_2024_combat_profile import build_rowan_2024_combat_profiles

        return [
            *build_lyra_2024_combat_profiles(),
            *build_thalen_2024_combat_profiles(),
            *build_mara_quickstep_combat_profiles(20),
            *build_rowan_2024_combat_profiles(),
            *build_kael_2024_combat_profiles(),
            *build_aurelia_2024_combat_profiles(),
        ]
    except Exception:
        logger.exception("Failed to build the 2024 pregen combat-profile registry.")
        raise
