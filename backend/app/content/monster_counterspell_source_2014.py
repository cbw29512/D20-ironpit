"""Immutable 2014 prepared Counterspell source proof (not a combat resolver).

This verifies *spell casting provenance* before the shared reaction-interrupt
engine may bind the source. No state changes and no fake admission of monsters.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)
_SPELL_ID = "counterspell"
_PRINTED_NAME = "counterspell"
_PRINTED_LEVEL = 3


def source_proves_prepared_counterspell_2014(monster: SourceMonster2014) -> bool:
    """Prove the exact printed prepared spell without monster-name dispatch."""
    try:
        source = monster.spellcasting
        if (
            "Spellcasting" not in monster.trait_names
            or not isinstance(source, dict)
            or source.get("source_complete") is not True
            or not isinstance(source.get("spells"), list)
        ):
            return False
        entries = [
            item for item in source["spells"]
            if isinstance(item, dict) and item.get("id") == _SPELL_ID
        ]
        if len(entries) != 1:
            return False
        entry = entries[0]
        if (
            set(entry) != {"id", "name", "level"}
            or entry.get("name") != _PRINTED_NAME
            or type(entry.get("level")) is not int
            or entry["level"] != _PRINTED_LEVEL
        ):
            return False

        sections = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        printed = sections.get("Spellcasting", "")
        if not printed:
            return False
        # Some SRD lists are an adjacent HTML <ul> rather than a paragraph.
        # Capture ONLY an immediately adjacent list, never unrelated traits.
        original = monster.source_traits or ""
        header = re.search(
            r"<p>[^<]*(?:<em>)?<strong>Spellcasting\.</strong>.*?</p>",
            original, flags=re.S | re.I,
        )
        if header:
            adjacent = re.match(
                r"\s*<ul>.*?</ul>", original[header.end():], flags=re.S,
            )
            if adjacent:
                printed += " " + re.sub(r"<[^>]*>", " ", adjacent.group())
        return bool(re.search(
            r"(?<![a-z])" + re.escape(_PRINTED_NAME) + r"(?![a-z])",
            " ".join(printed.casefold().split()),
        ))
    except Exception:
        logger.exception(
            "Could not certify prepared Counterspell source for %s", monster.id,
        )
        raise
