from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Iron Pit arena policy is universal. These names describe mechanics that remain
# preserved in source provenance but cannot execute inside the pocket dimension.
_ARENA_DISABLED_ACTION_PATTERNS = (
    re.compile(r"\b(?:summon|conjure|spawn|split|duplicate|animate)\b", re.I),
    re.compile(r"\b(?:teleport|plane shift|dimension door|misty step|ethereal(?:ness)?)\b", re.I),
    re.compile(r"\b(?:banish|banishment)\b", re.I),
    re.compile(r"\billusory appearance\b", re.I),
    # The standard Pit has no underwater environment and permits no destructible terrain.
    re.compile(r"\b(?:ink cloud|wall of ice)\b", re.I),
)

ARENA_OUT_OF_SCOPE_TRAITS_2014 = frozenset({
    "Earth Glide",
    "Ethereal Jaunt",
    "False Appearance",
    "Hellish Rejuvenation",
    "Hellish Restoration",
    "Incorporeal Movement",
    "Mimicry",
    "Rejuvenation",
    "Siege Monster",
    "Spider Climb",
    "Web Sense",
    "Web Walker",
})


def is_arena_disabled_action_2014(name: str) -> bool:
    """Return True only for actions explicitly disabled by Iron Pit arena policy."""
    try:
        return any(pattern.search(name) is not None for pattern in _ARENA_DISABLED_ACTION_PATTERNS)
    except Exception as exc:
        logger.exception("Failed to classify 2014 arena action %r.", name)
        raise ValueError(f"Could not classify 2014 arena action {name!r}.") from exc


def usable_movement_speed_2014(mode: str, speed_ft: int) -> int:
    """Apply arena movement restrictions without mutating source monster data."""
    try:
        if speed_ft < 0:
            raise ValueError("Movement speed cannot be negative.")
        return 0 if mode == "burrow" else speed_ft
    except Exception as exc:
        logger.exception("Failed to apply Iron Pit movement policy to %s=%s.", mode, speed_ft)
        raise ValueError(f"Could not apply Iron Pit movement policy to {mode!r}.") from exc
