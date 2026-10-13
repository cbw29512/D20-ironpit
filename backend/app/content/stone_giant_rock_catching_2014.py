from __future__ import annotations

import logging

from app.domain.reactions import AttackDamageReductionReaction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def build_stone_giant_rock_catching() -> AttackDamageReductionReaction:
    """Bind 2014 Stone Giant Rock Catching to the universal attack-damage reduction Reaction.

    Source-derived: Reaction, DC 10 Dexterity save vs qualifying ranged attack hit;
    success negates the damage. Iron Pit simplification broadens printed rock/hurled
    objects to eligible ranged attack hits. AoE/save spells remain excluded by attack_kinds.
    """
    try:
        return AttackDamageReductionReaction(
            source_id="rock-catching",
            source_name="Rock Catching",
            attack_kinds=["ranged"],
            required_damage_types=[DamageType.BLUDGEONING],
            reduction_dice_count=0,
            reduction_dice_size=2,
            save_ability="dexterity",
            save_dc=10,
            negate_on_success=True,
        )
    except Exception as exc:
        logger.exception("Failed to bind 2014 Stone Giant Rock Catching.")
        raise RuntimeError("2014 Stone Giant Rock Catching binding failed.") from exc
