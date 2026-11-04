from __future__ import annotations

import logging

from app.content.monster_innate_source_corrections_2014 import (
    corrected_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

ARENA_NEUTRAL_INNATE_SPELLS_2014 = frozenset({
    "alarm",
    "animal-friendship",
    "animal-messenger",
    "animate-dead",
    "arcane-lock",
    "arcanists-magic-aura",
    "augury",
    "beast-sense",
    "clairvoyance",
    "commune",
    "commune-with-nature",
    "comprehend-languages",
    "contact-other-plane",
    "continual-flame",
    "control-water",
    "control-weather",
    "control-winds",
    "create-food-and-water",
    "create-or-destroy-water",
    "creation",
    "dancing-lights",
    "detect-evil-and-good",
    "detect-magic",
    "detect-poison-and-disease",
    "detect-thoughts",
    "dimension-door",
    "disguise-self",
    "divination",
    "dream",
    "druidcraft",
    "earthquake",
    "enlarge-reduce",
    "fabricate",
    "feather-fall",
    "feign-death",
    "find-the-path",
    "find-traps",
    "floating-disk",
    "geas",
    "gentle-repose",
    "glyph-of-warding",
    "goodberry",
    "guards-and-wards",
    "hallucinatory-terrain",
    "heroes-feast",
    "identify",
    "illusory-script",
    "legend-lore",
    "leomunds-secret-chest",
    "leomunds-tiny-hut",
    "levitate",
    "light",
    "locate-animals-or-plants",
    "locate-creature",
    "locate-object",
    "longstrider",
    "mage-hand",
    "magic-mouth",
    "magnificent-mansion",
    "major-image",
    "meld-into-stone",
    "mending",
    "message",
    "mind-blank",
    "minor-illusion",
    "mirage-arcane",
    "mislead",
    "misty-step",
    "mordenkainens-magnificent-mansion",
    "mordenkainens-private-sanctum",
    "move-earth",
    "nondetection",
    "nystuls-magic-aura",
    "pass-without-trace",
    "passwall",
    "plane-shift",
    "plant-growth",
    "prestidigitation",
    "private-sanctum",
    "produce-flame",
    "programmed-illusion",
    "project-image",
    "protection-from-poison",
    "purify-food-and-drink",
    "raise-dead",
    "rarys-telepathic-bond",
    "remove-curse",
    "resurrection",
    "rope-trick",
    "scrying",
    "secret-chest",
    "seeming",
    "sending",
    "shillelagh",
    "silence",
    "silent-image",
    "spare-the-dying",
    "speak-with-animals",
    "speak-with-dead",
    "speak-with-plants",
    "spike-growth",
    "stone-shape",
    "stoneskin",
    "symbol",
    "telekinesis",
    "telepathy",
    "teleport",
    "thaumaturgy",
    "time-stop",
    "tiny-hut",
    "tongues",
    "transmute-rock",
    "tree-stride",
    "true-seeing",
    "unseen-servant",
    "wall-of-thorns",
    "water-breathing",
    "water-walk",
    "wind-walk",
    "wish",
    "zone-of-truth",
    "})",
})",
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
