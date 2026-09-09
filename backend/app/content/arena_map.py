from __future__ import annotations

import logging

from app.domain.grid import BattleMapDefinition

logger = logging.getLogger(__name__)


def build_standard_iron_pit_map() -> BattleMapDefinition:
    """Return the approved single Iron Pit VTT battlefield: 24 x 16 five-foot squares."""
    try:
        return BattleMapDefinition(
            id="iron-pit-standard-vtt",
            width_squares=24,
            height_squares=16,
            cell_size_ft=5,
        )
    except Exception:
        logger.exception("Failed to build the standard Iron Pit VTT map definition.")
        raise
