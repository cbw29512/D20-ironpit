from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.domain.encounters import EncounterCombatant
from app.domain.persistent_save_zones import PersistentSaveZoneState
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def member_in_save_zone(member: EncounterCombatant, zone: PersistentSaveZoneState) -> bool:
    try:
        if member.state.position is None:
            return False
        return footprint_distance_ft(
            member.state.position,
            member.state.template.size,
            zone.position,
            CreatureSize.MEDIUM,
        ) <= zone.radius_ft
    except Exception:
        logger.exception("Failed save-zone occupancy check for %s.", member.combatant_id)
        raise
