from __future__ import annotations

import logging

from app.combat.area_shapes import cell_center_ft, radius_contains
from app.combat.debuff_counters import difficult_terrain_multiplier
from app.combat.grid_geometry import occupied_cells
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.spells import SpellSaveAction
from app.domain.temporary_terrain import TemporaryTerrainZone

logger = logging.getLogger(__name__)


def cell_is_difficult_terrain(
    zones: list[TemporaryTerrainZone],
    cell: GridPosition,
    mover: EncounterCombatant,
) -> bool:
    """Return whether a cell is covered by an active magical Difficult Terrain zone."""
    try:
        point = cell_center_ft(cell.x, cell.y)
        for zone in zones:
            center = cell_center_ft(zone.center.x, zone.center.y)
            if not radius_contains(center, point, zone.radius_ft):
                continue
            if difficult_terrain_multiplier(mover.state, source_is_magical=zone.source_is_magical) > 1:
                return True
        return False
    except Exception:
        logger.exception("Failed Difficult Terrain cell check for %s.", mover.combatant_id)
        raise


def destination_is_difficult_terrain(
    zones: list[TemporaryTerrainZone],
    mover: EncounterCombatant,
    destination: GridPosition,
) -> bool:
    try:
        return any(
            cell_is_difficult_terrain(zones, GridPosition(x=x, y=y), mover)
            for x, y in occupied_cells(destination, mover.state.template.size)
        )
    except Exception:
        logger.exception("Failed Difficult Terrain destination check for %s.", mover.combatant_id)
        raise


def apply_spell_difficult_terrain(
    setup: EncounterSetup,
    caster: EncounterCombatant,
    action: SpellSaveAction,
    center: GridPosition,
    round_number: int,
) -> TemporaryTerrainZone | None:
    """Place the printed temporary Difficult Terrain overlay after a qualifying save spell."""
    try:
        if not action.creates_difficult_terrain:
            return None
        radius = action.area.radius_ft if action.area is not None else action.area_radius_ft
        if radius is None:
            raise ValueError(f"{action.name} creates Difficult Terrain without area radius.")
        zone = TemporaryTerrainZone(
            zone_id=f"{caster.combatant_id}:{action.id}:{round_number}:{len(setup.temporary_terrain_zones) + 1}",
            source_id=caster.combatant_id,
            action_id=action.id,
            action_name=action.name,
            center=center.model_copy(deep=True),
            radius_ft=radius,
            expires_round=round_number + action.difficult_terrain_duration_rounds,
        )
        setup.temporary_terrain_zones.append(zone)
        return zone
    except Exception:
        logger.exception("Failed to apply Difficult Terrain for %s.", action.id)
        raise


def expire_source_terrain(setup: EncounterSetup, source_id: str, round_number: int) -> list[str]:
    """End source-owned terrain at the printed source-turn-end expiry."""
    try:
        remaining: list[TemporaryTerrainZone] = []
        expired: list[str] = []
        for zone in setup.temporary_terrain_zones:
            if (
                zone.source_id == source_id
                and zone.expiry_timing == "source_turn_end"
                and round_number >= zone.expires_round
            ):
                expired.append(zone.zone_id)
                continue
            remaining.append(zone)
        setup.temporary_terrain_zones = remaining
        return expired
    except Exception:
        logger.exception("Failed to expire Difficult Terrain for %s.", source_id)
        raise
