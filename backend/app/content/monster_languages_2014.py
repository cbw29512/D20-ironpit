"""Conservative 2014 SRD language extraction for source-owned combat cards.

Only explicit names and the printed "(usually Common)" default are treated
as known languages. Telepathy is not spoken language. Unresolved choices and
unidentified historical/creator languages fail closed instead of guessing.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

# Explicit spoken and understood language names in the 2014 pinned corpus.
_KNOWN = (
    "abyssal", "aquan", "auran", "celestial", "common", "deep speech",
    "draconic", "druidic", "dwarvish", "elvish", "giant", "gnomish",
    "goblin", "halfling", "ignan", "infernal", "orc", "primordial",
    "sphinx", "sylvan", "terran", "thieves' cant", "undercommon",
    "blink dog", "giant eagle", "giant elk", "giant owl",
)
_PATTERN = re.compile(
    r"(?<![A-Za-z])(?:"
    + "|".join(re.escape(value) for value in sorted(_KNOWN, key=len, reverse=True))
    + r")(?![A-Za-z])",
    re.IGNORECASE,
)
_CANNOT_SPEAK = re.compile(
    r"(?:can't|cannot|doesn't|does not|can't|couldn't)\s+speak"
    r"|without (?:the ability to )?speak",
    re.IGNORECASE,
)


def source_languages_2014(monster: SourceMonster2014) -> tuple[list[str], list[str]]:
    """Return explicit (spoken, understood) sets; no synthetic assumptions."""
    try:
        raw = (monster.languages or "").strip()
        if not raw or raw in {"--", "—", "-"}:
            return [], []
        matches = {match.group(0).casefold() for match in _PATTERN.finditer(raw)}
        if re.search(r"\ball\s*(?:,|$)", raw, re.IGNORECASE):
            matches.add("all")
        # A printed free choice is unknown unless the source supplies a default.
        # "Any one language (usually Common)" explicitly identifies Common.
        # Other unspecified "Any N" options are intentionally not fabricated.
        if raw.casefold().startswith(("any ", "one language", "the languages", "a language")):
            if "(usually common)" not in raw.casefold():
                matches.clear()
        understood = sorted(matches)
        spoken = [] if _CANNOT_SPEAK.search(raw) else list(understood)
        return spoken, understood
    except Exception:
        logger.exception("2014 source language binding failed for %s.", monster.id)
        raise
