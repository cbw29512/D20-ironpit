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
)
_ARENA_DISABLED_EQUIPMENT_ACTIONS = frozenset({"Antennae"})
_EQUIPMENT_REFERENCE = re.compile(
    r"\b(?:armor|armour|shield|weapon|equipment|object(?:s)?(?: made of)? metal|metal object(?:s)?)\b", re.I,
)
_EQUIPMENT_DEGRADATION = re.compile(
    r"\b(?:corrod\w*|rust\w*|dissolv\w*|destroy\w*|permanent\w*|cumulative|penalty)\b", re.I,
)
_CREATURE_EFFECT = re.compile(
    r"\b(?:saving throw|escape dc|hit points?|target takes|creature takes|grappled|restrained|poisoned|"
    r"blinded|stunned|prone|frightened|paralyzed|unconscious|swallowed)\b",
    re.I,
)

# These traits are preserved as source truth but cannot alter an Iron Pit result
# under the universal pocket-dimension rules. They therefore never block a card.
ARENA_OUT_OF_SCOPE_TRAITS_2014 = frozenset({
    "Corrode Metal",
    "Earth Glide",
    "Ethereal Jaunt",
    "False Appearance",
    "Hellish Rejuvenation",
    "Hellish Restoration",
    "Incorporeal Movement",
    "Iron Scent",
    "Mimicry",
    "Rejuvenation",
    "Rust Metal",
    "Siege Monster",
    "Web Sense",
    "Web Walker",
})

# These remain usable source mechanics, but the existing movement engine already
# carries their only meaningful arena consequence. They must not be treated as
# disabled simply because the Pit prevents unreachable wall/altitude states.
ARENA_USABLE_MOVEMENT_TRAITS_2014 = frozenset({"Spider Climb"})


def is_arena_disabled_action_2014(name: str) -> bool:
    """Return True only for actions explicitly disabled by Iron Pit arena policy."""
    try:
        return name in _ARENA_DISABLED_EQUIPMENT_ACTIONS or any(
            pattern.search(name) is not None for pattern in _ARENA_DISABLED_ACTION_PATTERNS
        )
    except Exception as exc:
        logger.exception("Failed to classify 2014 arena action %r.", name)
        raise ValueError(f"Could not classify 2014 arena action {name!r}.") from exc


def is_arena_disabled_attack_detail_2014(text: str | None) -> bool:
    """Ignore only residual attack text whose remaining effect is equipment degradation."""
    try:
        if not text:
            return False
        return bool(
            _EQUIPMENT_REFERENCE.search(text)
            and _EQUIPMENT_DEGRADATION.search(text)
            and not _CREATURE_EFFECT.search(text)
        )
    except Exception as exc:
        logger.exception("Failed to classify 2014 attack residual %r.", text)
        raise ValueError("Could not classify 2014 attack residual.") from exc


def usable_movement_speed_2014(mode: str, speed_ft: int) -> int:
    """Apply arena movement restrictions without mutating source monster data."""
    try:
        if speed_ft < 0:
            raise ValueError("Movement speed cannot be negative.")
        return 0 if mode == "burrow" else speed_ft
    except Exception as exc:
        logger.exception("Failed to apply Iron Pit movement policy to %s=%s.", mode, speed_ft)
        raise ValueError(f"Could not apply Iron Pit movement policy to {mode!r}.") from exc
