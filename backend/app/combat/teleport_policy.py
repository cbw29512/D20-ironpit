from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance
from app.combat.grid_geometry import footprint_distance_ft, position_in_bounds
from app.combat.grid_pathing_support import overlapping_occupants
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.teleport_actions import TeleportAction

logger = logging.getLogger(__name__)


def choose_teleport_destination(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: TeleportAction,
) -> GridPosition | None:
    try:
        if setup.map_definition is None or caster.state.position is None:
            return None
        enemies = setup.monsters if caster.side == "heroes" else setup.heroes
        living = [
            enemy for enemy in enemies
            if enemy.state.is_alive and not enemy.state.is_dead and enemy.state.position is not None
        ]
        if not living:
            return None
        target = min(living, key=lambda enemy: (combatant_distance(caster, enemy), enemy.combatant_id))
        if combatant_distance(caster, target) <= 5:
            return None
        members = [*setup.heroes, *setup.monsters]
        best: GridPosition | None = None
        best_key = None
        width = setup.map_definition.width_squares
        height = setup.map_definition.height_squares
        for x in range(width):
            for y in range(height):
                destination = GridPosition(x=x, y=y)
                if not position_in_bounds(setup.map_definition, destination, caster.state.template.size):
                    continue
                if overlapping_occupants(caster, destination, members):
                    continue
                if footprint_distance_ft(
                    caster.state.position,
                    caster.state.template.size,
                    destination,
                    caster.state.template.size,
                ) > action.range_ft:
                    continue
                distance = footprint_distance_ft(
                    destination,
                    caster.state.template.size,
                    target.state.position,
                    target.state.template.size,
                )
                key = (distance, x, y)
                if best_key is None or key < best_key:
                    best = destination
                    best_key = key
        return best
    except Exception:
        logger.exception("Failed to choose teleport destination for %s.", caster.combatant_id)
        raise


def choose_teleport_action(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> tuple[TeleportAction, GridPosition] | None:
    """Arena AI never selects teleport or plane shift. The pit forbids those options."""
    try:
        if caster is None or setup is None or not str(turn_key or "").strip():
            raise ValueError("Teleport choice requires a caster, setup, and turn key.")
        return None
    except Exception:
        logger.exception("Failed teleport choice for %s.", getattr(caster, "combatant_id", "?"))
        raise
