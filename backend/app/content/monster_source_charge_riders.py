from __future__ import annotations

import logging
import re

from app.domain.charge import ChargeDamage, ChargeProfile
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

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


def _damage(match: re.Match[str]) -> ChargeDamage:
    bonus = int(match.group("mod") or 0) * (-1 if match.group("sign") == "-" else 1)
    return ChargeDamage(
        dice_count=int(match.group("count")),
        dice_size=int(match.group("size")),
        damage_bonus=bonus,
        damage_type=match.group("type").lower(),
    )


def _split_replacement_delta(
    replacement: ChargeDamage,
    *,
    base_dice_count: int | None,
    base_dice_size: int | None,
    base_damage_bonus: int | None,
    base_damage_type: str | None,
) -> tuple[str, ChargeDamage]:
    same_family = (
        base_dice_count is not None
        and base_dice_size == replacement.dice_size
        and base_damage_bonus == replacement.damage_bonus
        and base_damage_type is not None
        and base_damage_type.lower() == replacement.damage_type.lower()
        and replacement.dice_count > base_dice_count
    )
    if not same_family:
        return "replacement_damage", replacement
    return "bonus_damage", replacement.model_copy(update={
        "dice_count": replacement.dice_count - base_dice_count,
        "damage_bonus": 0,
    })


def parse_charge_replacement(
    text: str,
    *,
    base_dice_count: int | None = None,
    base_dice_size: int | None = None,
    base_damage_bonus: int | None = None,
    base_damage_type: str | None = None,
) -> ChargeProfile | None:
    try:
        replacement_match = _CHARGE_REPLACEMENT.search(text)
        prone = _CHARGE_PRONE.search(text)
        if replacement_match is None and prone is None:
            return None
        distances = [int(match.group("distance")) for match in (replacement_match, prone) if match is not None]
        updates: dict[str, object] = {"minimum_move_ft": min(distances)}
        if prone is not None:
            maximum = CreatureSize(prone.group("size").lower())
            updates["max_target_size"] = maximum
            updates["prone_max_target_size"] = maximum
        if replacement_match is not None:
            field, damage = _split_replacement_delta(
                _damage(replacement_match),
                base_dice_count=base_dice_count,
                base_dice_size=base_dice_size,
                base_damage_bonus=base_damage_bonus,
                base_damage_type=base_damage_type,
            )
            updates[field] = damage
        return ChargeProfile(**updates)
    except (TypeError, ValueError):
        logger.exception("Failed to parse source charge rider: %r", text)
        raise


__all__ = ["parse_charge_replacement"]