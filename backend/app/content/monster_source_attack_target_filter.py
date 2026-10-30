from __future__ import annotations

import logging
import re

from app.domain.target_filters import TargetFilter

logger = logging.getLogger(__name__)

_CREATURE_TYPES = {
    "aberration", "beast", "celestial", "construct", "dragon", "elemental", "fey",
    "fiend", "giant", "humanoid", "monstrosity", "ooze", "plant", "undead",
}


def source_target_filter(text: str) -> TargetFilter:
    """Parse source creature-type/tag eligibility without ability-name dispatch."""
    try:
        required_types: set[str] = set()
        excluded_types: set[str] = set()
        excluded_tags: set[str] = set()

        required = re.search(r"\bIf the target is an? ([A-Za-z]+)\b", text, re.IGNORECASE)
        if required:
            normalized = required.group(1).lower()
            if normalized in _CREATURE_TYPES:
                required_types.add(normalized)

        for match in re.finditer(r"\bnon-([A-Za-z]+)\s+creature\b", text, re.IGNORECASE):
            excluded_types.add(match.group(1).lower())

        excluded = re.search(
            r"\bisn[’']t\s+an?\s+([A-Za-z]+)(?:\s+or\s+([A-Za-z]+))?",
            text,
            re.IGNORECASE,
        )
        if excluded:
            for value in (excluded.group(1), excluded.group(2)):
                if not value:
                    continue
                normalized = value.lower()
                (excluded_types if normalized in _CREATURE_TYPES else excluded_tags).add(normalized)

        return TargetFilter(
            required_creature_types=sorted(required_types),
            excluded_creature_types=sorted(excluded_types),
            excluded_tags=sorted(excluded_tags),
        )
    except Exception as exc:
        logger.exception("Failed to parse source target filter.")
        raise RuntimeError("Source target filter could not be parsed.") from exc


__all__ = ["source_target_filter"]
