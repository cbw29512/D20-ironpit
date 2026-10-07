from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider

logger = logging.getLogger(__name__)
_MARTIAL_ADVANTAGE = "Martial Advantage"
_DAMAGE_DICE = re.compile(
    r"Martial Advantage\..*?extra\s+\d+\s+\((\d+)d(\d+)\)\s+damage",
    re.IGNORECASE | re.DOTALL,
)
_ADJACENCY = re.compile(
    r"within\s+5\s+feet\s+of\s+an\s+ally.*?isn['’]t\s+incapacitated",
    re.IGNORECASE | re.DOTALL,
)


def martial_advantage_rider_2014(
    monster: SourceMonster2014,
) -> OncePerTurnWeaponHitDamageRider | None:
    """Compile printed Martial Advantage into a shared adjacent-ally hit rider."""
    try:
        if _MARTIAL_ADVANTAGE not in monster.trait_names:
            return None
        source = monster.source_traits or ""
        damage = _DAMAGE_DICE.search(source)
        if damage is None or _ADJACENCY.search(source) is None:
            raise ValueError(f"{monster.name} has unsupported Martial Advantage wording.")
        count, size = int(damage.group(1)), int(damage.group(2))
        return OncePerTurnWeaponHitDamageRider(
            source_id="martial-advantage",
            source_name=_MARTIAL_ADVANTAGE,
            dice_count=count,
            dice_size=size,
            requires_active_ally_adjacent_to_target=True,
        )
    except Exception:
        logger.exception("Failed to bind 2014 Martial Advantage for %s.", monster.name)
        raise
