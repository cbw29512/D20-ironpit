"""Reusable link between persistent spell save zones and temporary terrain.

Immutable Action declarations request terrain. Each cast creates one linked,
fight-local terrain overlay which follows its parent zone's lifetime.
"""
from __future__ import annotations

import logging

from app.domain.encounters import EncounterSetup
from app.domain.persistent_save_zones import (
    PersistentSaveZoneAction, PersistentSaveZoneState,
)
from app.domain.temporary_terrain import TemporaryTerrainZone

logger = logging.getLogger(__name__)


def apply_persistent_zone_terrain(
    setup: EncounterSetup,
    action: PersistentSaveZoneAction,
    zone: PersistentSaveZoneState,
) -> TemporaryTerrainZone | None:
    """Attach the existing Difficult Terrain primitive to a source-neutral zone."""
    try:
        if not action.creates_difficult_terrain:
            return None
        if action.follows_source or zone.follows_source:
            raise ValueError("Moving zone terrain is unsupported without dynamic geometry.")
        terrain = TemporaryTerrainZone(
            zone_id=f"{zone.zone_id}:terrain",
            persistent_zone_id=zone.zone_id,
            source_id=zone.source_id,
            action_id=zone.action_id,
            action_name=zone.action_name,
            center=zone.position.model_copy(deep=True),
            radius_ft=zone.radius_ft,
            source_is_magical=zone.save_context != "nonmagical",
            expires_round=zone.expires_round,
        )
        setup.temporary_terrain_zones.append(terrain)
        return terrain
    except Exception:
        logger.exception("Could not attach persistent zone terrain to %s.", zone.zone_id)
        raise


def sync_persistent_zone_terrain(setup: EncounterSetup) -> None:
    """Remove terrain only when its exact parent persistent zone is no longer live."""
    try:
        live_ids = {zone.zone_id for zone in setup.save_zones}
        setup.temporary_terrain_zones = [
            terrain for terrain in setup.temporary_terrain_zones
            if terrain.persistent_zone_id is None
            or terrain.persistent_zone_id in live_ids
        ]
    except Exception:
        logger.exception("Could not reconcile persistent-zone terrain lifecycle.")
        raise
