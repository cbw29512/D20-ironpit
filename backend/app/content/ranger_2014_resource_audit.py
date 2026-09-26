from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_RANGER_2014_SLOTS = {
    1: (),
    2: (2,), 3: (3,), 4: (3,),
    5: (4, 2), 6: (4, 2), 7: (4, 3), 8: (4, 3),
    9: (4, 3, 2), 10: (4, 3, 2), 11: (4, 3, 3), 12: (4, 3, 3),
    13: (4, 3, 3, 1), 14: (4, 3, 3, 1), 15: (4, 3, 3, 2), 16: (4, 3, 3, 2),
    17: (4, 3, 3, 3, 1), 18: (4, 3, 3, 3, 1), 19: (4, 3, 3, 3, 2), 20: (4, 3, 3, 3, 2),
}


def ranger_2014_spell_slot_resources(level: int) -> dict[str, int]:
    """Independently certify 2014 Ranger spell-slot resources by class level."""
    try:
        slots = _RANGER_2014_SLOTS.get(level)
        if slots is None:
            raise ValueError("2014 Ranger resource audit covers levels 1 through 20.")
        return {
            f"spell-slot-{spell_level}": uses
            for spell_level, uses in enumerate(slots, start=1)
            if uses > 0
        }
    except Exception:
        logger.exception("Failed to certify 2014 Ranger resources at level %s.", level)
        raise
