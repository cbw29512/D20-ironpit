from __future__ import annotations

import re

_ON_HIT_SAVE_BLOCK = re.compile(
    r"(?:(?:If|The target)[^.]*following effect\.\s*)?"
    r"(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*DC\s*\d+[^.]*\.\s*"
    r"(?:(?:First )?Failure):\s*[^.]+\."
    r"(?:\s*[^.]*repeats the save[^.]*\.)?"
    r"(?:\s*Second Failure:\s*[^.]+\.)?"
    r"(?:\s*Failure by \d+ or More:\s*[^.]+\.\s*While [^.]+\.)?",
    re.I,
)


def attack_rider_text(actions: str, match: re.Match[str]) -> str:
    """Return the complete source rider text, including a following on-hit save block."""
    text = match.group("tail") or ""
    following = actions[match.end():].lstrip()
    save_block = _ON_HIT_SAVE_BLOCK.match(following)
    if save_block:
        return text + ". " + save_block.group(0)
    if re.match(r"(?:If|Until|The target|Whenever|While)\b", following, re.I):
        text += ". " + following.split(".", 1)[0]
    return text


__all__ = ["attack_rider_text"]
