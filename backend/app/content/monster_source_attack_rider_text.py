from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_ON_HIT_SAVE_BLOCK = re.compile(
    r"(?:(?:If|The target)[^.]*following effect\.\s*)?"
    r"(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*DC\s*\d+[^.]*\.\s*"
    r"(?:(?:First )?Failure):\s*[^.]+\."
    r"(?:\s*[^.]*repeats the save[^.]*\.)?"
    r"(?:\s*Second Failure:\s*[^.]+\.)?"
    r"(?:\s*Failure by \d+ or More:\s*[^.]+\.\s*While [^.]+\.)?"
    r"(?:\s*While wounded,[^.]+\.\s*The wound closes after [^.]+\.)?",
    re.IGNORECASE,
)


def attack_rider_text(actions: str, match: re.Match[str]) -> str:
    try:
        text = match.group("tail") or ""
        following = actions[match.end():].lstrip()
        save_block = _ON_HIT_SAVE_BLOCK.match(following)
        if save_block:
            return text + ". " + save_block.group(0)
        if re.match(r"(?:If|Until|The target|Whenever|While)\b", following, re.IGNORECASE):
            text += ". " + following.split(".", 1)[0]
        return text
    except Exception as exc:
        logger.exception("Failed to extract source attack rider text.")
        raise RuntimeError("Source attack rider text could not be extracted.") from exc
