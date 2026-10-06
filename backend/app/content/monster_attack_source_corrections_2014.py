from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014

logger = logging.getLogger(__name__)

_SCOUT_LONGBOW_SIGNATURE = (
    "Longbow", "ranged", 4,
    6, 1, 8, 2, "piercing",
)
_SCOUT_LONGBOW_RANGE = (150, 600)


def corrected_attack_range_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> tuple[int | None, int | None]:
    """Apply reviewed 2014 parser range corrections without mutating source data."""
    try:
        current = (attack.normal_range_ft, attack.long_range_ft)
        if (monster.id, attack.id) != ("scout", "longbow"):
            return current

        signature = (
            attack.name, attack.kind, attack.attack_bonus,
            attack.damage.average, attack.damage.dice_count,
            attack.damage.dice_size, attack.damage.bonus, attack.damage.type,
        )
        if signature != _SCOUT_LONGBOW_SIGNATURE:
            raise RuntimeError(
                f"2014 Scout Longbow source drift: {signature!r} != "
                f"{_SCOUT_LONGBOW_SIGNATURE!r}"
            )
        if current == _SCOUT_LONGBOW_RANGE:
            return current
        if current[0] not in (None, _SCOUT_LONGBOW_RANGE[0]) or current[1] not in (
            None, _SCOUT_LONGBOW_RANGE[1]
        ):
            raise RuntimeError(
                f"2014 Scout Longbow range drift: {current!r} is not a partial "
                f"{_SCOUT_LONGBOW_RANGE!r} parse."
            )
        return _SCOUT_LONGBOW_RANGE
    except Exception:
        logger.exception(
            "Failed to apply 2014 attack-range source correction for %s/%s.",
            monster.id,
            attack.id,
        )
        raise
