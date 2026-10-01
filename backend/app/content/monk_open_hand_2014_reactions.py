from __future__ import annotations

import logging

from app.domain.reactions import AttackDamageReductionReaction

logger = logging.getLogger(__name__)


def build_monk_2014_attack_damage_reduction(
    level: int,
) -> AttackDamageReductionReaction | None:
    """Bind 2014 Deflect Missiles to the universal attack-damage reduction Reaction."""
    try:
        if level < 3:
            return None
        return AttackDamageReductionReaction(
            source_id="deflect-missiles",
            source_name="Deflect Missiles",
            attack_kinds=["ranged"],
            reduction_dice_count=1,
            reduction_dice_size=10,
            reduction_ability="dexterity",
            add_level=True,
        )
    except Exception as exc:
        logger.exception("Failed to bind 2014 Monk Deflect Missiles at level %s.", level)
        raise RuntimeError("2014 Monk Deflect Missiles binding failed.") from exc
