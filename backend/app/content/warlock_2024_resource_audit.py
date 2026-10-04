from __future__ import annotations

import logging

from app.content.class_spell_progression import mystic_arcanum_levels
from app.content.warlock_combat_levels import WARLOCK_COMBAT_LEVELS
from app.domain.character_builds import CharacterBuildProfile

logger = logging.getLogger(__name__)


def warlock_2024_resources(profile: CharacterBuildProfile) -> dict[str, int]:
    """Return independently certified finite 2024 Warlock resources by class level."""
    try:
        level = profile.level
        row = WARLOCK_COMBAT_LEVELS[level]
        resources = {f"spell-slot-{row.pact_slot_level}": row.pact_slots}
        if level >= 6:
            resources["dark-ones-own-luck"] = max(1, profile.final_ability_scores.modifier("charisma"))
        for spell_level in mystic_arcanum_levels(level):
            resources[f"mystic-arcanum-{spell_level}"] = 1
        return resources
    except Exception:
        logger.exception("Failed to derive 2024 Warlock resources at level %s.", profile.level)
        raise
