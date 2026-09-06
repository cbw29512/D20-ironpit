from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)
_GRAPPLE = re.compile(
    r"\bIf the target is a (Tiny|Small|Medium|Large|Huge|Gargantuan) or smaller creature,\s*"
    r"it has the Grappled condition\s*\(escape DC\s*(\d+)\)", re.I,
)
_PRONE = re.compile(
    r"\bIf the target is a (Tiny|Small|Medium|Large|Huge|Gargantuan) or smaller creature,\s*"
    r"it has the Prone condition\b", re.I,
)
_NEXT_ATTACK_DISADVANTAGE = re.compile(
    r"(?:has|gains?)\s+Disadvantage\s+on\s+(?:the|its)\s+next\s+attack\s+roll"
    r"(?:\s+it\s+makes)?\s+before\s+the\s+end\s+of\s+its\s+next\s+turn", re.I,
)
_MAX_HP_REDUCTION = re.compile(
    r"Hit Point maximum\s+(?:decreases|is reduced)\s+by an amount equal to\s+"
    r"(?:the\s+)?(?:(Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder)\s+)?damage taken",
    re.I,
)


def parse_hit_riders(block: str) -> list[dict[str, object]]:
    """Compile source attack riders by mathematical outcome; unknown prose remains audited elsewhere."""
    try:
        effects: list[dict[str, object]] = []
        grapple = _GRAPPLE.search(block)
        if grapple:
            max_size, escape_dc = grapple.groups()
            effects.append({"kind": "grapple", "escape_dc": int(escape_dc), "max_target_size": max_size.lower()})
        prone = _PRONE.search(block)
        if prone:
            effects.append({"kind": "prone", "max_target_size": prone.group(1).lower()})
        if _NEXT_ATTACK_DISADVANTAGE.search(block):
            effects.append({"kind": "next-attack-disadvantage", "expires_at_end_of_target_turn": True})
        max_hp = _MAX_HP_REDUCTION.search(block)
        if max_hp:
            effect: dict[str, object] = {"kind": "max-hp-reduction"}
            if max_hp.group(1):
                effect["damage_type"] = max_hp.group(1).lower()
            effects.append(effect)
        return effects
    except (AttributeError, TypeError, ValueError):
        logger.exception("Failed to compile source-backed attack riders from %r", block)
        raise
