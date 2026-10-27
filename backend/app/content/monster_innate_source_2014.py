from __future__ import annotations

import logging

from app.content.monster_innate_source_corrections_2014 import (
    corrected_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

ARENA_NEUTRAL_INNATE_SPELLS_2014 = frozenset({
    "detect-evil-and-good",
    "druidcraft",
    "pass-without-trace",
    "disguise-self",
    "scrying",
    "detect-thoughts",
    "detect-magic",
    "mage-hand",
    "minor-illusion",
    "nondetection",
    "plane-shift",
    "geas",
})
PIT_BANNED_INNATE_SPELLS_2014 = frozenset({
    "teleport",
    "plane-shift",
    "dimension-door",
    "misty-step",
})
DISPEL_ATTACKER_TYPES_2014 = (
    "celestial", "elemental", "fey", "fiend", "undead",
)


def innate_spellcasting_source_2014(
    monster: SourceMonster2014,
) -> dict[str, object] | None:
    """Return the immutable parsed view, applying reviewed source repair when needed."""
    try:
        return corrected_innate_spellcasting_2014(monster)
    except Exception:
        logger.exception(
            "Failed to load 2014 innate spellcasting source for %s.", monster.id
        )
        raise


def innate_spells_2014(monster: SourceMonster2014) -> list[dict[str, object]]:
    try:
        data = innate_spellcasting_source_2014(monster)
        if data is None:
            return []
        spells = data.get("spells") or []
        if not isinstance(spells, list):
            raise ValueError(f"{monster.name} innate spell list is not structured.")
        return [item for item in spells if isinstance(item, dict)]
    except Exception:
        logger.exception("Failed to read 2014 innate spell list for %s.", monster.id)
        raise


def innate_spell_save_dc_2014(monster: SourceMonster2014) -> int | None:
    try:
        data = innate_spellcasting_source_2014(monster)
        if data is None:
            return None
        raw = data.get("save_dc")
        return int(raw) if raw is not None else None
    except Exception:
        logger.exception("Failed to read 2014 innate spell save DC for %s.", monster.id)
        raise
