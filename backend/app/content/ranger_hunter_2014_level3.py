from __future__ import annotations

import logging

from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider

logger = logging.getLogger(__name__)


def colossus_slayer_2014() -> OncePerTurnWeaponHitDamageRider:
    """Compile Colossus Slayer into the shared once-per-turn weapon-hit rider."""
    try:
        return OncePerTurnWeaponHitDamageRider(
            source_id="colossus-slayer",
            source_name="Colossus Slayer",
            dice_count=1,
            dice_size=8,
            damage_type=None,
            requires_target_below_max_hp=True,
        )
    except Exception:
        logger.exception("Failed to compile 2014 Colossus Slayer.")
        raise
