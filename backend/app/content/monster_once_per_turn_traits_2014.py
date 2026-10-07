from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider

logger = logging.getLogger(__name__)
_MARTIAL_ADVANTAGE = "Martial Advantage"
_MARTIAL_BODY = re.compile(
    r"Martial Advantage\.</strong></em>\s*(.*?)</p>",
    re.IGNORECASE | re.DOTALL,
)
_ONCE_PER_TURN = re.compile(r"\bonce\s+per\s+turn\b", re.IGNORECASE)
_WEAPON_HIT = re.compile(r"hits?\s+with\s+a\s+weapon\s+attack\b", re.IGNORECASE)
_DAMAGE_DICE = re.compile(
    r"extra\s+\d+\s+\((\d+)d(\d+)\)\s+damage",
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
        body_match = _MARTIAL_BODY.search(source)
        if body_match is None:
            raise ValueError(f"{monster.name} has no isolated Martial Advantage source body.")
        body = body_match.group(1)
        damage = _DAMAGE_DICE.search(body)
        if (
            _ONCE_PER_TURN.search(body) is None
            or _WEAPON_HIT.search(body) is None
            or damage is None
            or _ADJACENCY.search(body) is None
        ):
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
