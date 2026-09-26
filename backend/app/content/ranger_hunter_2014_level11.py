from __future__ import annotations

import logging

from app.domain.area_weapon_attacks import AreaWeaponAttackAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def volley_2014(attack_id: str, range_ft: int) -> AreaWeaponAttackAction:
    """Compile Hunter Volley as a universal point-origin area weapon attack."""
    try:
        return AreaWeaponAttackAction(
            id="volley",
            name="Volley",
            attack_id=attack_id,
            range_ft=range_ft,
            area=AreaTargeting(shape="radius", origin="point", radius_ft=10),
            source="D&D Basic Rules 2014: Hunter 11",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Hunter Volley.")
        raise
