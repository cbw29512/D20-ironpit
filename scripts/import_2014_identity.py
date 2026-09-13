from __future__ import annotations

import re

CREATURE_TYPES = (
    "aberration", "beast", "celestial", "construct", "dragon", "elemental", "fey",
    "fiend", "giant", "humanoid", "monstrosity", "ooze", "plant", "undead",
)


def parse_identity(meta: str) -> tuple[str, str, list[str], str | None]:
    """Return canonical base type plus exact printed type/subtypes/alignment from a 2014 meta line."""
    size, separator, remainder = meta.partition(" ")
    if not separator or not size:
        raise ValueError(f"Malformed 2014 monster meta line: {meta!r}")
    type_text, comma, alignment = remainder.partition(",")
    printed = type_text.strip()
    if not comma or not printed:
        raise ValueError(f"Malformed 2014 monster type/alignment: {meta!r}")

    lowered = printed.lower()
    base = next((kind for kind in CREATURE_TYPES if re.search(rf"\b{re.escape(kind)}s?\b", lowered)), None)
    if base is None:
        raise ValueError(f"Unknown 2014 creature type in {meta!r}")

    subtype_match = re.search(r"\(([^)]+)\)", printed)
    subtypes = [] if subtype_match is None else [item.strip().lower() for item in subtype_match.group(1).split(",") if item.strip()]
    return base, printed, subtypes, alignment.strip() or None
