from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.domain.encounters import EncounterCombatant
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)

MELEE_ENGAGEMENT_FT = 5


def _living_enemies(
    mover: EncounterCombatant,
    members: list[EncounterCombatant],
) -> list[EncounterCombatant]:
    return [
        member
        for member in members
        if member.combatant_id != mover.combatant_id
        and member.side != mover.side
        and member.state.is_alive
        and not member.state.is_dead
        and member.state.position is not None
    ]


def nearest_living_enemy_distance_ft(
    mover: EncounterCombatant,
    members: list[EncounterCombatant],
    origin: GridPosition | None = None,
) -> int | None:
    """Return the closest living enemy footprint distance from origin or the mover."""
    try:
        start = origin if origin is not None else mover.state.position
        if start is None:
            return None
        distances = [
            footprint_distance_ft(
                start,
                mover.state.template.size,
                enemy.state.position,
                enemy.state.template.size,
            )
            for enemy in _living_enemies(mover, members)
            if enemy.state.position is not None
        ]
        return min(distances) if distances else None
    except Exception:
        logger.exception("Failed nearest-enemy distance for %s.", mover.combatant_id)
        raise


def voluntary_destination_leaves_melee(
    mover: EncounterCombatant,
    members: list[EncounterCombatant],
    destination: GridPosition,
) -> bool:
    """True when voluntary movement would leave an existing melee engagement."""
    try:
        current = nearest_living_enemy_distance_ft(mover, members)
        if current is None or current > MELEE_ENGAGEMENT_FT:
            return False
        after = nearest_living_enemy_distance_ft(mover, members, destination)
        return after is not None and after > current
    except Exception:
        logger.exception("Failed melee-engagement lock for %s.", mover.combatant_id)
        raise
