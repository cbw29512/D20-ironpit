"""Source-bound parser for the 327 printed SRD 5.1 monster Languages entries.

An unselected choice or unknown past-life language is never presumed Common.
Telepathy is not a spoken language for the purpose of Command.
"""
from __future__ import annotations

import logging
import re

from app.domain.languages import LanguageProfile

logger = logging.getLogger(__name__)
_NAMES = frozenset({
    "abyssal", "aquan", "auran", "celestial", "common", "deep speech",
    "draconic", "druidic", "dwarvish", "elvish", "giant", "gnoll",
    "gnomish", "goblin", "halfling", "ignan", "infernal", "orc",
    "primordial", "sahuagin", "sphinx", "sylvan", "terran",
    "undercommon", "yeti", "otyugh", "worg", "winter wolf",
    "blink dog", "giant eagle", "giant elk", "giant owl", "thieves' cant",
})
_UNRESOLVED = re.compile(
    r"\bany (?:one|two|four|six|languages)\b|\bup to\b|"
    r"\bknew in life\b|\bcreator\b|\bone language known\b",
    re.IGNORECASE,
)
_TELEPATHY = re.compile(r"\btelepathy\s+\d+\s*ft\.", re.IGNORECASE)
_CAN_NOT_SPEAK = re.compile(
    r"\b(?:can't|cannot|doesn't|does not) speak\b", re.IGNORECASE,
)
_END_CLAUSE = re.compile(
    r"\s+but\s+(?:can't|cannot|doesn't|does not) speak\b.*$", re.IGNORECASE,
)
_PLUS = re.compile(r"\s+plus\s+.*$", re.IGNORECASE)
_BRACKET = re.compile(r"\s*\([^)]*\)")
_SPLIT = re.compile(r"\s*(?:,|\band\b)\s*", re.IGNORECASE)


def _languages(text: str) -> tuple[tuple[str, ...], bool]:
    try:
        found: set[str] = set()
        unresolved = False
        for name in _SPLIT.split(text.strip(" ,.")):
            name = name.strip(" ,.").casefold()
            if not name:
                continue
            if name in _NAMES:
                found.add(name)
            else:
                unresolved = True
        return tuple(sorted(found)), unresolved
    except Exception:
        logger.exception("Could not parse 2014 printed language names: %r.", text)
        raise


def monster_languages_2014(value: str) -> LanguageProfile:
    """Extract only confirmed speech/comprehension; preserve source ambiguity."""
    try:
        raw = " ".join(value.replace("canât", "can't").split())
        if raw in {"--", "—", "-"}:
            return LanguageProfile(unspecified=False)
        if not raw:
            return LanguageProfile()
        if raw.casefold().startswith("understands commands given in any language"):
            return LanguageProfile(understands_all=True, unspecified=False)
        without_telepathy = _TELEPATHY.sub("", raw).strip(" ,.")
        if without_telepathy.casefold() == "all":
            return LanguageProfile(
                speaks_all=True, understands_all=True, unspecified=False,
            )
        unresolved = bool(_UNRESOLVED.search(without_telepathy))
        no_speech = bool(_CAN_NOT_SPEAK.search(without_telepathy))
        beast_form = "(can't speak in " in without_telepathy.casefold()
        text = _PLUS.sub("", _END_CLAUSE.sub("", _BRACKET.sub("", without_telepathy)))
        text = text.strip()
        parts = re.split(r"\bunderstands\b", text, maxsplit=1, flags=re.IGNORECASE)
        spoken, unknown_spoken = _languages(parts[0])
        understood, unknown_understood = _languages(parts[1] if len(parts) == 2 else "")
        if len(parts) == 2 and spoken and understood:
            # 'Giant Eagle understands Common ... but can't speak them':
            # the named species language remains spoken.
            pass
        elif no_speech or beast_form:
            if not understood:
                understood = spoken
            spoken = ()
        return LanguageProfile(
            spoken=spoken,
            understood=tuple(sorted(set(spoken) | set(understood))),
            unspecified=unresolved or unknown_spoken or unknown_understood,
        )
    except Exception:
        logger.exception("Failed to preserve 2014 source language evidence: %r.", value)
        raise
