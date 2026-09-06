from __future__ import annotations

import re

from app.content.monster_combat_scope import combat_math_relevant

_OBJECT_END_DAMAGE = re.compile(
    r"\bThe\s+\w+\s+takes\s+\d+(?:\s*\([^)]*\))?\s+[A-Za-z]+\s+damage\s+if\s+it\s+ends\s+its\s+turn\s+inside\s+an\s+object\. ?",
    re.IGNORECASE,
)
_SUNLIGHT_SENTENCE = re.compile(
    r"\bWhile\s+in\s+sunlight,\s+[^.]*\. ?",
    re.IGNORECASE,
)


def arena_neutral_trait_source(source: object) -> bool:
    """True when all combat math in a trait depends on triggers absent from the standard open Pit."""
    text = re.sub(r"\s+", " ", str(source or "")).strip()
    if not text:
        return True
    scoped = _OBJECT_END_DAMAGE.sub("", text)
    scoped = _SUNLIGHT_SENTENCE.sub("", scoped)
    return not combat_math_relevant(scoped)
