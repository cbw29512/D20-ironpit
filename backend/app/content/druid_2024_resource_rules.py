from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def druid_wild_shape_uses(level: int) -> int:
    try:
        if not 1 <= level <= 20:
            raise ValueError("2024 Druid Wild Shape progression covers levels 1 through 20.")
        if level == 1:
            return 0
        if level <= 5:
            return 2
        if level <= 16:
            return 3
        return 4
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve 2024 Druid Wild Shape uses for level %s.", level)
        raise ValueError(f"Failed to resolve 2024 Druid Wild Shape uses for level {level}.") from exc


def druid_wild_resurgence_slot_restore_uses(level: int) -> int:
    try:
        return 1 if level >= 5 else 0
    except Exception as exc:
        logger.exception("Failed to resolve 2024 Wild Resurgence uses for level %s.", level)
        raise ValueError(f"Failed to resolve 2024 Wild Resurgence uses for level {level}.") from exc


def druid_nature_magician_uses(level: int) -> int:
    try:
        return 1 if level >= 20 else 0
    except Exception as exc:
        logger.exception("Failed to resolve 2024 Nature Magician uses for level %s.", level)
        raise ValueError(f"Failed to resolve 2024 Nature Magician uses for level {level}.") from exc


def land_natural_recovery_free_cast_uses(level: int) -> int:
    try:
        return 1 if level >= 6 else 0
    except Exception as exc:
        logger.exception("Failed to resolve 2024 Natural Recovery uses for level %s.", level)
        raise ValueError(f"Failed to resolve 2024 Natural Recovery uses for level {level}.") from exc
