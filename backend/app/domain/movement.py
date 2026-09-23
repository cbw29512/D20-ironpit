from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
MovementMode = Literal["walk", "fly", "climb", "swim", "burrow"]


class MovementModes(BaseModel):
    """Complete movement fingerprint retained from a creature stat block."""

    walk_ft: int = Field(ge=0)
    fly_ft: int = Field(default=0, ge=0)
    climb_ft: int = Field(default=0, ge=0)
    swim_ft: int = Field(default=0, ge=0)
    burrow_ft: int = Field(default=0, ge=0)
    hover: bool = False


def preferred_horizontal_mode(modes: MovementModes) -> MovementMode:
    """Choose the normal Iron Pit horizontal mode; flight stays horizontal but remains flight."""
    try:
        if modes.fly_ft > 0 and modes.fly_ft >= modes.walk_ft:
            return "fly"
        return "walk"
    except Exception:
        logger.exception("Failed to choose preferred horizontal movement mode.")
        raise


def preferred_horizontal_speed(modes: MovementModes) -> int:
    """Return the printed speed for the preferred horizontal movement mode."""
    try:
        mode = preferred_horizontal_mode(modes)
        return modes.fly_ft if mode == "fly" else modes.walk_ft
    except Exception:
        logger.exception("Failed to resolve preferred horizontal movement speed.")
        raise
