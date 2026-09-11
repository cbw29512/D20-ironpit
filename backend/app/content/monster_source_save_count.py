from __future__ import annotations

import re

_SAVING_THROW = re.compile(
    r"\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+Saving Throw:",
    re.IGNORECASE,
)
_SENTENCE_START = re.compile(r"(?:^|\.\s+)([^.]+)\.\s*$", re.DOTALL)


def _previous_sentence(text: str, start: int) -> str:
    prefix = text[:start].rstrip()
    match = _SENTENCE_START.search(prefix)
    return match.group(1).strip() if match else prefix.rsplit(".", 1)[-1].strip()


def _is_out_of_match_save(text: str, start: int) -> bool:
    previous = _previous_sentence(text, start)
    return bool(re.search(
        r"\b(?:finishes?|after finishing)\s+(?:a|its)\s+Long Rest\b",
        previous,
        re.IGNORECASE,
    ))


def source_action_save_count(actions: str) -> int:
    """Count saving throws that can actually resolve during an Iron Pit action sequence."""
    return sum(
        not _is_out_of_match_save(actions, match.start())
        for match in _SAVING_THROW.finditer(actions)
    )
