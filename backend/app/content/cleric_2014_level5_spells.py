from __future__ import annotations

import logging

from app.content.shared_healing_spells_2014 import (
    mass_cure_wounds_2014 as shared_mass_cure_wounds_2014,
)
from app.domain.actions import HealingAction

logger = logging.getLogger(__name__)


def mass_cure_wounds_2014(
    wisdom_modifier: int,
    slot_level: int = 5,
) -> HealingAction:
    """Compile Life Cleric Mass Cure Wounds with Disciple of Life."""
    try:
        if wisdom_modifier < 0:
            raise ValueError("2014 Mass Cure Wounds requires a nonnegative Wisdom modifier.")
        return shared_mass_cure_wounds_2014(
            wisdom_modifier,
            slot_level,
            additional_healing_bonus=2 + slot_level,
        )
    except Exception:
        logger.exception("Failed to compile 2014 Life Cleric Mass Cure Wounds at slot level %s.", slot_level)
        raise
