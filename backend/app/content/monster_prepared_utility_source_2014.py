"""2014 prepared utility spell source proofs for formation-only Iron Pit.

Schema: immutable SourceMonster2014.spellcasting entries + printed Spellcasting
text. State: none. Utility spells are source metadata only, not fake Actions.
This module deliberately does NOT alter the shared prepared binder while older
draft PRs #1081 and #1159 still touch that file.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Printed D&D 2014 spell name and level. No monster-identity dispatch.
_ARENA_INERT_PREPARED_2014: dict[str, tuple[str, int]] = {
    "detect-magic": ("detect magic", 1),
    "mage-hand": ("mage hand", 0),
}


def source_proven_prepared_utility_spells_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Recognize harmless spell IDs without inventing combat actions.

    Detect Magic identifies nearby magic, but does not reveal an invisible
    creature's position or grant a combat modifier. Mage Hand's 10-pound
    manipulation cannot attack, activate magic items, or supply an extra
    combat attack under the locked arena policy. Other spells stay blocked.
    """
    try:
        source = monster.spellcasting
        if (
            "Spellcasting" not in monster.trait_names
            or not isinstance(source, dict)
            or source.get("source_complete") is not True
            or not isinstance(source.get("spells"), list)
        ):
            return frozenset()

        sections = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        printed = " ".join(sections.get("Spellcasting", "").casefold().split())
        if not printed:
            return frozenset()

        accepted: set[str] = set()
        seen: set[str] = set()
        for entry in source["spells"]:
            if not isinstance(entry, dict):
                return frozenset()
            spell_id = entry.get("id")
            if spell_id not in _ARENA_INERT_PREPARED_2014:
                continue
            expected_name, expected_level = _ARENA_INERT_PREPARED_2014[spell_id]
            if (
                spell_id in seen
                or set(entry) != {"id", "name", "level"}
                or entry.get("name") != expected_name
                or type(entry.get("level")) is not int
                or entry["level"] != expected_level
            ):
                return frozenset()
            seen.add(spell_id)
            # Search only the complete Spellcasting source section; an
            # unrelated trait mentioning a utility spell cannot prove it.
            if not re.search(
                r"(?<![a-z])" + re.escape(expected_name) + r"(?![a-z])",
                printed,
            ):
                return frozenset()
            accepted.add(spell_id)
        return frozenset(accepted)
    except Exception:
        logger.exception(
            "Failed prepared utility source proof for %s", monster.id,
        )
        raise
