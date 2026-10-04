from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.size import CreatureSize
from app.domain.suppression_zones import PersistentSuppressionZoneState

logger = logging.getLogger(__name__)


def member_in_zone(member: EncounterCombatant, zone: PersistentSuppressionZoneState) -> bool:
    try:
        if member.state.position is None:
            return False
        return footprint_distance_ft(
            member.state.position,
            member.state.template.size,
            zone.position,
            CreatureSize.TINY,
        ) <= zone.radius_ft
    except Exception:
        logger.exception("Failed suppression-zone occupancy check for %s.", member.combatant_id)
        raise


def covering_zones(member: EncounterCombatant, setup: EncounterSetup) -> list[PersistentSuppressionZoneState]:
    try:
        return [zone for zone in setup.suppression_zones if member_in_zone(member, zone)]
    except Exception:
        logger.exception("Failed to list covering suppression zones for %s.", member.combatant_id)
        raise


def verbal_casting_blocked(member: EncounterCombatant, setup: EncounterSetup) -> bool:
    try:
        return any(zone.blocks_verbal_spells for zone in covering_zones(member, setup))
    except Exception:
        logger.exception("Failed verbal-casting suppression check for %s.", member.combatant_id)
        raise


def zone_center_legal(setup: EncounterSetup, position: GridPosition, cast_range_ft: int, caster: EncounterCombatant) -> bool:
    try:
        if setup.map_definition is None or caster.state.position is None:
            return False
        from app.combat.grid_geometry import position_in_bounds

        if not position_in_bounds(setup.map_definition, position, CreatureSize.TINY):
            return False
        return footprint_distance_ft(
            caster.state.position,
            caster.state.template.size,
            position,
            CreatureSize.TINY,
        ) <= cast_range_ft
    except Exception:
        logger.exception("Failed suppression-zone placement legality for %s.", caster.combatant_id)
        raise
