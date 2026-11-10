"""Shared validator for periodic and damage-triggered repeated saving throws."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def validate_repeat_save_fields(
    ability: str | None,
    dc: int | None,
    timing: str | None,
    damage_trigger: str,
) -> None:
    """A damage-only trigger requires an ability/DC, never a fake turn timing."""
    try:
        has_ability = ability is not None
        has_dc = dc is not None
        has_timing = timing is not None
        if has_ability != has_dc:
            raise ValueError("Repeat-save fields require ability and DC together.")
        if has_timing and not has_ability:
            raise ValueError("Periodic repeat saves require ability and DC.")
        if has_ability and not has_timing and damage_trigger == "none":
            raise ValueError("Repeat saves require a periodic timing or damage trigger.")
        if damage_trigger != "none" and not has_ability:
            raise ValueError("Damage repeat saves require ability and DC.")
    except Exception:
        logger.exception("Invalid repeat-save schema: timing=%s, trigger=%s.",
                         timing, damage_trigger)
        raise
