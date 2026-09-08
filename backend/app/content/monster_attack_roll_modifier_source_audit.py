from __future__ import annotations

import re

from app.domain.weapons import ConditionalAttackModifier

_SUPPORTED = re.compile(
    r"\(with\s+(?P<mode>Advantage|Disadvantage)\s+if\s+the\s+target\s+doesn[’']t\s+have\s+all\s+its\s+Hit\s+Points\)",
    re.I,
)
_ANY_CONDITIONAL = re.compile(
    r"\b(?:Melee|Ranged|Melee or Ranged)\s+Attack Roll:\s*[+-]?\d+\s*\([^)]*\b(?:Advantage|Disadvantage)\b[^)]*\)",
    re.I,
)


def parse_attack_roll_modifier(clause: str) -> ConditionalAttackModifier | None:
    try:
        match = _SUPPORTED.fullmatch(clause.strip())
        if match is None:
            return None
        return ConditionalAttackModifier(
            trigger="target_missing_hp",
            mode=match.group("mode").lower(),
        )
    except Exception as exc:
        raise ValueError("conditional attack roll modifier could not be parsed") from exc


def unsupported_conditional_attack_modifier(actions: str) -> bool:
    try:
        stripped = _SUPPORTED.sub("", actions)
        return bool(_ANY_CONDITIONAL.search(stripped))
    except Exception as exc:
        raise ValueError("conditional attack roll modifier audit failed") from exc
