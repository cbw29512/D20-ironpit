from __future__ import annotations

import logging

from app.content.warlock_2014_progression import warlock_2014_level

logger = logging.getLogger(__name__)


def warlock_2014_resources(level: int) -> dict[str, int]:
    """Return independently certified finite 2014 Warlock resources by class level."""
    try:
        row = warlock_2014_level(level)
        resources = {f"spell-slot-{row.pact_slot_level}": row.pact_slots}
        if level >= 6:
            resources["dark-ones-own-luck"] = 1
        for spell_level in row.mystic_arcanum_levels:
            resources[f"mystic-arcanum-{spell_level}"] = 1
        if level >= 14:
            resources["hurl-through-hell"] = 1
        if level >= 20:
            resources["eldritch-master"] = 1
        return resources
    except Exception:
        logger.exception("Failed to derive 2014 Warlock resources at level %s.", level)
        raise
