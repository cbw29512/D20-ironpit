from __future__ import annotations

import re

_SAVING_THROW = re.compile(
    r"\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+Saving Throw:",
    re.IGNORECASE,
)
_SENTENCE_START = re.compile(r"(?:^|\.\s+)([^.]+)\.\s*$", re.DOTALL)
_REPEAT_TIMING = re.compile(
    r"\b(?:at\s+the\s+(?:start|end)\s+of|every\s+\d+\s+hours?|after\s+finishing|"
    r"finishes?)\b",
    re.IGNORECASE,
)
_REPEAT_LANGUAGE = re.compile(
    r"\b(?:repeat(?:s|ed|ing)?|again|subsequent)\b",
    re.IGNORECASE,
)


def _previous_sentence(text: str, start: int) -> str:
    prefix = text[:start].rstrip()
    match = _SENTENCE_START.search(prefix)
    return match.group(1).strip() if match else prefix.rsplit(".", 1)[-1].strip()


def _context(text: str, start: int) -> str:
    return text[max(0, start - 220):start].rsplit(".", 1)[-1].strip()


def _is_out_of_match_save(text: str, start: int) -> bool:
    previous = _previous_sentence(text, start)
    return bool(re.search(
        r"\b(?:finishes?|after finishing)\s+(?:a|its)\s+Long Rest\b",
        previous,
        re.IGNORECASE,
    ))


def _is_repeat_save(text: str, start: int) -> bool:
    context = _context(text, start)
    if _REPEAT_LANGUAGE.search(context):
        return True
    if _REPEAT_TIMING.search(context) and re.search(
        r"\b(?:turn|round|hours?|Long Rest)\b", context, re.IGNORECASE,
    ):
        return True
    return False


def source_action_save_count(actions: str) -> int:
    """Count initial saves that resolve from Iron Pit actions, not lifecycle repeats."""
    return sum(
        not _is_out_of_match_save(actions, match.start())
        and not _is_repeat_save(actions, match.start())
        for match in _SAVING_THROW.finditer(actions)
    )
