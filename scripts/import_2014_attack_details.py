from __future__ import annotations

import re

DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
}
_ROLLED = re.compile(
    r"(?:,?\s*(?:plus|and)\s+)(\d+)\s*\((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\)\s*([A-Za-z]+) damage",
    re.I,
)
_FIXED = re.compile(r"(?:,?\s*(?:plus|and)\s+)(\d+)\s+([A-Za-z]+) damage", re.I)


def _rolled(match: re.Match[str]) -> dict | None:
    average, count, size, sign, bonus, damage_type = match.groups()
    damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES:
        return None
    return {
        "average": int(average),
        "dice_count": int(count),
        "dice_size": int(size),
        "bonus": int(bonus or 0) * (-1 if sign == "-" else 1),
        "type": damage_type,
    }


def _fixed(match: re.Match[str]) -> dict | None:
    amount, damage_type = match.groups()
    damage_type = damage_type.lower()
    if damage_type not in DAMAGE_TYPES:
        return None
    return {"average": int(amount), "dice_count": 0, "dice_size": 6, "bonus": int(amount), "type": damage_type}


def parse_secondary_damage(remainder: str) -> tuple[list[dict], str]:
    extras: list[dict] = []

    def replace_rolled(match: re.Match[str]) -> str:
        parsed = _rolled(match)
        if parsed is None:
            return match.group(0)
        extras.append(parsed)
        return " "

    def replace_fixed(match: re.Match[str]) -> str:
        parsed = _fixed(match)
        if parsed is None:
            return match.group(0)
        extras.append(parsed)
        return " "

    residual = _ROLLED.sub(replace_rolled, remainder)
    residual = _FIXED.sub(replace_fixed, residual)
    residual = re.sub(r"^[\s,;]*(?:and\s+)?|[\s,;]+$", "", residual, flags=re.I)
    return extras, residual.strip(" .")
