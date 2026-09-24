from __future__ import annotations

import logging

from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)
_SOURCE = "D&D Basic Rules 2014 / SRD 5.1"


def _cantrip_dice(character_level: int) -> int:
    try:
        if character_level not in range(1, 21):
            raise ValueError("Cantrip character level must be between 1 and 20.")
        return 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)
    except Exception:
        logger.exception("Failed to resolve 2014 cantrip scaling at level %s.", character_level)
        raise


def fire_bolt_2014(attack_bonus: int, character_level: int) -> SpellAttackAction:
    try:
        return SpellAttackAction(
            id="fire-bolt", name="Fire Bolt", level=0, action_cost="action",
            attack_kind="ranged", range_ft=120, attack_bonus=attack_bonus,
            damage_dice_count=_cantrip_dice(character_level), damage_dice_size=10,
            damage_type="fire", animation="fire-bolt", source=f"{_SOURCE}: Fire Bolt",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Fire Bolt at character level %s.", character_level)
        raise


def produce_flame_2014(attack_bonus: int, character_level: int) -> SpellAttackAction:
    try:
        return SpellAttackAction(
            id="produce-flame", name="Produce Flame", level=0, action_cost="action",
            attack_kind="ranged", range_ft=30, attack_bonus=attack_bonus,
            damage_dice_count=_cantrip_dice(character_level), damage_dice_size=8,
            damage_type="fire", animation="produce-flame", source=f"{_SOURCE}: Produce Flame",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Produce Flame at character level %s.", character_level)
        raise
