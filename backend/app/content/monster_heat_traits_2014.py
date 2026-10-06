from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_HEATED_BODY = "Heated Body"
_HEATED_WEAPONS = "Heated Weapons"
_HEATED_BODY_DAMAGE = re.compile(
    r"Heated Body\..*?takes\s+\d+\s*\((\d+)d(\d+)\)\s+fire damage",
    re.IGNORECASE | re.DOTALL,
)
_HEATED_WEAPON_DAMAGE = re.compile(
    r"Heated Weapons\..*?extra\s+\d+\s*\((\d+)d(\d+)\)\s+fire damage.*?included in the attack",
    re.IGNORECASE | re.DOTALL,
)


def heated_body_action_2014(monster: SourceMonster2014) -> TimedSelfBuffAction | None:
    """Bind source-owned contact heat to the shared melee-hit retaliation primitive."""
    try:
        if _HEATED_BODY not in monster.trait_names:
            return None
        match = _HEATED_BODY_DAMAGE.search(monster.source_traits or "")
        if match is None:
            raise ValueError(f"{monster.name} Heated Body lacks a parseable fire-damage payload.")
        dice_count, dice_size = (int(match.group(1)), int(match.group(2)))
        return TimedSelfBuffAction(
            id=f"{monster.id}-heated-body",
            name=_HEATED_BODY,
            activation_timing="passive",
            melee_hit_retaliation=MeleeHitRetaliation(
                range_ft=5,
                dice_count=dice_count,
                dice_size=dice_size,
                damage_type=DamageType.FIRE,
            ),
            animation="heated-body",
        )
    except Exception:
        logger.exception("Failed to bind 2014 Heated Body for %s.", monster.name)
        raise


def supports_heated_weapons_2014(monster: SourceMonster2014) -> bool:
    """Certify that printed Heated Weapons damage is already present on source attacks."""
    try:
        if _HEATED_WEAPONS not in monster.trait_names:
            return False
        match = _HEATED_WEAPON_DAMAGE.search(monster.source_traits or "")
        if match is None:
            raise ValueError(f"{monster.name} Heated Weapons lacks a parseable included-damage payload.")
        dice_count, dice_size = (int(match.group(1)), int(match.group(2)))
        return any(
            isinstance(row, dict)
            and str(row.get("type", "")).lower() == "fire"
            and int(row.get("dice_count", 0)) == dice_count
            and int(row.get("dice_size", 0)) == dice_size
            for attack in monster.attacks
            for row in attack.on_hit_damage
        )
    except Exception:
        logger.exception("Failed to certify 2014 Heated Weapons for %s.", monster.name)
        raise


def bound_heat_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return heat traits fully represented by shared runtime/source-damage primitives."""
    try:
        bound: set[str] = set()
        if heated_body_action_2014(monster) is not None:
            bound.add(_HEATED_BODY)
        if supports_heated_weapons_2014(monster):
            bound.add(_HEATED_WEAPONS)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to classify 2014 heat traits for %s.", monster.name)
        raise
