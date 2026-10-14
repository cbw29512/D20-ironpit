from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.persistent_save_zones import PersistentSaveZoneState
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def member_in_save_zone(member: EncounterCombatant, zone: PersistentSaveZoneState, setup: EncounterSetup | None = None) -> bool:
    try:
        if member.state.position is None:
            return False
        center = zone.position
        if zone.follows_source:
            if setup is None:
                raise ValueError("Source-following zones require encounter state.")
            source = next((actor for actor in [*setup.heroes, *setup.monsters]
                           if actor.combatant_id == zone.source_id), None)
            if source is None or source.state.position is None:
                return False
            center = source.state.position
        return footprint_distance_ft(
            member.state.position,
            member.state.template.size,
            center,
            CreatureSize.MEDIUM,
        ) <= zone.radius_ft
    except Exception:
        logger.exception("Failed save-zone occupancy check for %s.", member.combatant_id)
        raise
