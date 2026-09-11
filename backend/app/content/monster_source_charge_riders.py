from __future__ import annotations

import re

from app.domain.charge import ChargeDamage, ChargeProfile

_CHARGE_REPLACEMENT = re.compile(
    r"\bor\s+\d+\s*\((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<mod>\d+))?\)\s*"
    r"(?P<type>[A-Za-z]+) damage if the [^.]+? moved (?P<distance>\d+)\+ feet straight toward the target immediately before the hit",
    re.I,
)


def parse_charge_replacement(text: str) -> ChargeProfile | None:
    match = _CHARGE_REPLACEMENT.search(text)
    if match is None:
        return None
    bonus = int(match.group("mod") or 0) * (-1 if match.group("sign") == "-" else 1)
    return ChargeProfile(
        minimum_move_ft=int(match.group("distance")),
        replacement_damage=ChargeDamage(
            dice_count=int(match.group("count")), dice_size=int(match.group("size")),
            damage_bonus=bonus, damage_type=match.group("type").lower(),
        ),
    )


__all__ = ["parse_charge_replacement"]