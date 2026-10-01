from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def monk_focus_points(level: int) -> int:
    """Return 2024 Monk Focus Points: none at level 1, then equal to Monk level."""
    try:
        if not 1 <= level <= 20:
            raise ValueError("2024 Monk Focus progression covers levels 1 through 20.")
        return level if level >= 2 else 0
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve 2024 Monk Focus Points for level %s.", level)
        raise ValueError(f"Failed to resolve 2024 Monk Focus Points for level {level}.") from exc


def uncanny_metabolism_uses(level: int) -> int:
    """Return the once-per-Long-Rest Uncanny Metabolism use from Monk level 2 onward."""
    try:
        if not 1 <= level <= 20:
            raise ValueError("2024 Monk Uncanny Metabolism progression covers levels 1 through 20.")
        return 1 if level >= 2 else 0
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve Uncanny Metabolism uses for level %s.", level)
        raise ValueError(f"Failed to resolve Uncanny Metabolism uses for level {level}.") from exc
