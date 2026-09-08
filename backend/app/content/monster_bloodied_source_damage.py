from __future__ import annotations

import re

from app.domain.models import ConditionalDamage, DamageType

_BLOODIED_REPLACEMENT = re.compile(
    r"\bor\s+\d+\s*\(\s*(?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s+"
    r"(?P<type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder)\s+damage\s+"
    r"if\b.*?\bBloodied\b",
    re.I,
)


def extract_bloodied_replacement(hit: str) -> tuple[str, ConditionalDamage | None]:
    """Extract an SRD Bloodied alternate weapon-damage clause from Hit text."""
    match = _BLOODIED_REPLACEMENT.search(hit)
    if match is None:
        return hit, None
    bonus = int(match.group("bonus") or 0) * (-1 if match.group("sign") == "-" else 1)
    conditional = ConditionalDamage(
        trigger="attacker_bloodied",
        mode="replace_weapon",
        dice_count=int(match.group("count")),
        dice_size=int(match.group("size")),
        damage_bonus=bonus,
        damage_type=DamageType(match.group("type").lower()),
    )
    prefix = hit[:match.start()].rstrip(" ,")
    suffix = hit[match.end():].lstrip(" ,")
    separator = ", " if prefix and suffix else ""
    return prefix + separator + suffix, conditional
