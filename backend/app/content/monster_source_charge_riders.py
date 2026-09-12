from __future__ import annotations

import re

from app.domain.charge import ChargeDamage, ChargeProfile
from app.domain.size import CreatureSize

_CHARGE_REPLACEMENT = re.compile(
    r"\bor\s+\d+\s*\((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<mod>\d+))?\)\s*"
    r"(?P<type>[A-Za-z]+) damage if the [^.]+? moved (?P<distance>\d+)\+ feet straight toward the target immediately before the hit",
    re.I,
)
_CHARGE_PRONE = re.compile(
    r"If the target is (?:a |an )?(?P<size>Tiny|Small|Medium|Large|Huge|Gargantuan) or smaller(?: creature)?,? "
    r"and the [^.]+? moved (?P<distance>\d+)\+ feet straight toward (?:it|the target) immediately before the hit, "
    r"the target has the Prone condition",
    re.I,
)


def parse_charge_replacement(text: str) -> ChargeProfile | None:
    replacement = _CHARGE_REPLACEMENT.search(text)
    prone = _CHARGE_PRONE.search(text)
    if replacement is None and prone is None:
        return None
    distances = [int(match.group("distance")) for match in (replacement, prone) if match is not None]
    updates: dict[str, object] = {"minimum_move_ft": min(distances)}
    if prone is not None:
        updates["prone_max_target_size"] = CreatureSize(prone.group("size").lower())
    if replacement is not None:
        bonus = int(replacement.group("mod") or 0) * (-1 if replacement.group("sign") == "-" else 1)
        updates["replacement_damage"] = ChargeDamage(
            dice_count=int(replacement.group("count")), dice_size=int(replacement.group("size")),
            damage_bonus=bonus, damage_type=replacement.group("type").lower(),
        )
    return ChargeProfile(**updates)


__all__ = ["parse_charge_replacement"]