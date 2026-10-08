from __future__ import annotations

from app.combat.grid_geometry import square_area_distance_ft, square_area_in_bounds
from app.combat.persistent_beneficial_zone_effects import zone_side_squares
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_beneficial_zones import PersistentBeneficialZoneAction


def beneficial_zone_position_legal(
    setup: EncounterSetup,
    position: GridPosition,
    action: PersistentBeneficialZoneAction,
) -> bool:
    return bool(
        setup.map_definition
        and square_area_in_bounds(
            setup.map_definition,
            position,
            zone_side_squares(action.length_ft),
        )
    )


def beneficial_zone_source_distance(
    caster: EncounterCombatant,
    position: GridPosition,
    action: PersistentBeneficialZoneAction,
) -> int:
    if caster.state.position is None:
        raise ValueError("Persistent beneficial zones require authoritative grid positions.")
    return square_area_distance_ft(
        caster.state.position,
        1,
        position,
        zone_side_squares(action.length_ft),
    )
