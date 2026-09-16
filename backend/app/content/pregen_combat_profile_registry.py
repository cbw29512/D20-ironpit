from __future__ import annotations

import logging

from app.content.fighter_2014_combat_profile import build_karnok_stoneward_2014_combat_profiles
from app.content.pregen_combat_profiles import PregenCombatProfile, _karnok_profile, _rokhan_profile, _seraphine_profile
from app.content.rogue_combat_fingerprint import build_mara_quickstep_combat_profile

logger = logging.getLogger(__name__)


def build_pregen_combat_profile_registry() -> dict[str, PregenCombatProfile]:
    """Assemble edition-specific fingerprints without inflating their schema module."""
    try:
        profiles = [
            *(_karnok_profile(level) for level in range(1, 13)),
            *(_rokhan_profile(level) for level in range(1, 7)),
            *(_seraphine_profile(level) for level in range(1, 5)),
            *build_karnok_stoneward_2014_combat_profiles(),
            build_mara_quickstep_combat_profile(),
        ]
        return {profile.template_id: profile for profile in profiles}
    except Exception:
        logger.exception("Failed to assemble pregen combat fingerprint registry.")
        raise
