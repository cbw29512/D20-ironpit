from __future__ import annotations

import re

STRUCTURED_FIELDS = ("traits", "actions", "bonusActions", "reactions", "legendaryActions")
_BARE_HEADING = re.compile(
    r"(?:[.!?])\s+(?P<heading>[A-Z][A-Za-z'’\-]*(?:\s+(?:[A-Z][A-Za-z'’\-]*|of|the|and)){0,4})\s*$"
)


def ends_with_heading(value: object, heading: str) -> bool:
    """Return True only when heading is a complete terminal token sequence."""
    text = str(value).strip()
    if not text or not heading:
        return False
    return bool(re.search(rf"(?:^|\s){re.escape(heading)}\s*$", text, re.IGNORECASE))


def longest_terminal_monster_name(
    value: object,
    monster_names: set[str],
    *,
    exclude_name: str = "",
) -> str | None:
    """Resolve suffix ambiguity by keeping only the longest exact monster-name match."""
    excluded = exclude_name.casefold()
    matches = [
        name
        for name in monster_names
        if name and name.casefold() != excluded and ends_with_heading(value, name)
    ]
    return max(matches, key=lambda name: (len(name), name.casefold())) if matches else None


def terminal_bare_heading(value: object) -> str | None:
    """Extract a short unpunctuated title-like heading appended after completed prose."""
    text = str(value).strip()
    if not text:
        return None
    match = _BARE_HEADING.search(text)
    return match.group("heading") if match else None


def strip_terminal_heading(value: object, heading: str) -> str:
    """Remove one exact terminal heading and preserve the completed prose before it."""
    text = str(value).rstrip()
    match = re.search(rf"(?:\s+){re.escape(heading)}\s*$", text, re.IGNORECASE)
    if match is None:
        raise ValueError(f"Expected terminal heading {heading!r}.")
    return text[: match.start()].rstrip()
