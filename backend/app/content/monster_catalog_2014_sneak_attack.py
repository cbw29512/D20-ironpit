from __future__ import annotations

import html
import re

_SNEAK_ATTACK = re.compile(
    r"Sneak Attack(?: \(1/Turn\))?\.\s*Once per turn,.*?extra\s+\d+\s*\((\d+)d6\)\s+damage",
    re.I | re.S,
)


def sneak_attack_d6_2014(source_traits: str | None) -> int:
    """Return source-declared monster Sneak Attack d6 count, failing closed on drift."""
    text = re.sub(r"<[^>]+>", " ", source_traits or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    if "Sneak Attack" not in text:
        return 0
    match = _SNEAK_ATTACK.search(text)
    if match is None:
        raise ValueError("2014 Sneak Attack source text did not match the certified parser.")
    return int(match.group(1))
