"""Source-proven 2014 physiology parameters for universal breath deprivation."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_HOLD_BREATH = re.compile(
    r"The [A-Za-z][A-Za-z '-]* can hold (?:its|his|her|their) breath for "
    r"(?P<amount>\\d+) (?P<unit>minute|minutes|hour|hours)\\.",
    re.IGNORECASE,
)
_NO_AIR = re.compile(
    r"\\b(?:doesn't|does not) (?:require air|need air|need to breathe)\\b",
    re.IGNORECASE,
)


def source_breath_hold_rounds_2014(monster: SourceMonster2014) -> int | None:
    """Read exact printed Hold Breath duration, rather than guessing from habitat."""
    try:
        if "Hold Breath" not in monster.trait_names:
            return None
        body = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Hold Breath", "").lstrip(": ")
        match = _HOLD_BREATH.fullmatch(body)
        if match is None:
            raise ValueError(f"Unsupported 2014 Hold Breath source for {monster.id}: {body!r}")
        amount = int(match.group("amount"))
        if amount < 1:
            raise ValueError(f"Nonpositive Hold Breath duration for {monster.id}.")
        # One combat round lasts six seconds. These values are immutable card data.
        return amount * (600 if match.group("unit").lower().startswith("hour") else 10)
    except Exception:
        logger.exception("Failed 2014 printed Hold Breath proof for %s.", monster.id)
        raise


def source_needs_air_2014(monster: SourceMonster2014) -> bool:
    """Explicit no-air source clauses override the default need to breathe."""
    try:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        # Printed Nature clauses can contain other independently handled traits.
        # We identify only the breathing fact, never grant extra mechanics.
        return not any(_NO_AIR.search(body) for body in sections.values())
    except Exception:
        logger.exception("Failed 2014 no-air source proof for %s.", monster.id)
        raise
