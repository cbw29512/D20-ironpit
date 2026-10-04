from __future__ import annotations

import logging

from app.content.warlock_2024_zone_spells import (
    fire_shield_2024,
    insect_plague_2024,
    stinking_cloud_2024,
    wall_of_fire_2024,
)

logger = logging.getLogger(__name__)


def build_varek_2024_save_zones(level: int, save_dc: int, pact_slot_level: int):
    try:
        zones = []
        if level >= 5:
            zones.append(stinking_cloud_2024(save_dc, pact_slot_level))
        if level >= 7:
            zones.append(wall_of_fire_2024(save_dc, pact_slot_level))
        if level >= 9:
            zones.append(insect_plague_2024(save_dc, pact_slot_level))
        return zones
    except Exception:
        logger.exception("Failed to bind 2024 Varek save zones at level %s.", level)
        raise


def build_varek_2024_self_buffs(level: int, pact_slot_level: int):
    try:
        if level < 7:
            return []
        return fire_shield_2024(pact_slot_level)
    except Exception:
        logger.exception("Failed to bind 2024 Varek self-buffs at level %s.", level)
        raise
