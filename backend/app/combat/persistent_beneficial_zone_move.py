from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.grid_geometry import footprint_distance_ft
from app.combat.persistent_beneficial_zone_effects import (
    sync_persistent_beneficial_zones,
    zone_footprint_size,
)
from app.combat.persistent_beneficial_zone_geometry import (
    beneficial_zone_position_legal,
    beneficial_zone_source_distance,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import BattleEvent
from app.domain.persistent_beneficial_zones import PersistentBeneficialZoneAction

logger = logging.getLogger(__name__)


def move_persistent_beneficial_zone(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: PersistentBeneficialZoneAction,
    zone_id: str,
    destination: GridPosition,
) -> tuple[BattleEvent, int]:
    try:
        zone = next(
            (
                item for item in setup.persistent_beneficial_zones
                if item.zone_id == zone_id and item.source_id == caster.combatant_id
            ),
            None,
        )
        if zone is None:
            raise ValueError(f"{action.name} has no active source-owned zone.")
        if action.move_action_cost is None or not is_available(caster.state, action.move_action_cost):
            raise ValueError(f"{action.name} move action is unavailable.")
        if not beneficial_zone_position_legal(setup, destination, action):
            raise ValueError(f"{action.name} move requires a legal in-bounds destination.")
        if beneficial_zone_source_distance(caster, destination, action) > action.move_range_ft:
            raise ValueError(f"{action.name} destination exceeds source range.")

        move_distance = footprint_distance_ft(
            zone.position,
            zone_footprint_size(zone.length_ft),
            destination,
            zone_footprint_size(action.length_ft),
        )
        if move_distance > action.move_distance_ft:
            raise ValueError(f"{action.name} cannot move that far.")

        spend(caster.state, action.move_action_cost)
        zone.position = destination.model_copy(deep=True)
        sync_persistent_beneficial_zones(setup, round_number)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            feature_id=action.id,
            animation=action.animation,
            description=f"{caster.state.template.name} moves {action.name}.",
        ), sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Persistent beneficial zone move failed for %s.", caster.combatant_id)
        raise RuntimeError("Persistent beneficial zone could not be moved.") from exc
