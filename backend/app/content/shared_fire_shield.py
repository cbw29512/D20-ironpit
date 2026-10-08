from __future__ import annotations

import logging

from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


def fire_shield_variants(slot_level: int) -> list[TimedSelfBuffAction]:
    """Shared 2014/2024 Fire Shield semantics; the caller supplies a legal slot."""
    try:
        if not 4 <= slot_level <= 9:
            raise ValueError("Fire Shield requires a fourth-level or higher legal spell slot.")
        variants = (
            ("warm", DamageType.COLD, DamageType.FIRE, 88),
            ("chill", DamageType.FIRE, DamageType.COLD, 87),
        )
        return [
            TimedSelfBuffAction(
                id=f"fire-shield-{variant}",
                name="Fire Shield",
                action_cost="action",
                resource_id=f"spell-slot-{slot_level}",
                resource_cost=1,
                duration_rounds=100,
                damage_resistances=[resistance],
                melee_hit_retaliation=MeleeHitRetaliation(
                    range_ft=5, dice_count=2, dice_size=8, damage_type=retaliation,
                ),
                ends_if_source_dead=True,
                expiry_timing="source_turn_end",
                priority=priority,
                selection_group="fire-shield-variants",
                selection_strategy="incoming-damage",
                animation="fire-shield",
            )
            for variant, resistance, retaliation, priority in variants
        ]
    except Exception:
        logger.exception("Could not assemble Fire Shield defense variants for slot %s.", slot_level)
        raise
