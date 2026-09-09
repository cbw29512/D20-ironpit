from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)
FRIGHTENED_EFFECT_ID = "frightened"


def distance_to_position(
    reactor: EncounterCombatant,
    mover: EncounterCombatant,
    mover_position: GridPosition,
) -> int:
    try:
        if reactor.state.position is None:
            raise ValueError(f"Reactor {reactor.combatant_id!r} has no grid position.")
        return footprint_distance_ft(
            reactor.state.position,
            reactor.state.template.size,
            mover_position,
            mover.state.template.size,
        )
    except Exception:
        logger.exception("Failed grid reaction distance for %s.", reactor.combatant_id)
        raise


def approaches_fear_source(
    mover: EncounterCombatant,
    destination: GridPosition,
    setup: EncounterSetup,
) -> bool:
    try:
        source_ids = {
            effect.source_id for effect in mover.state.timed_effects
            if effect.effect_id == FRIGHTENED_EFFECT_ID
        }
        if not source_ids:
            return False
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        if mover.state.position is None:
            raise ValueError(f"Mover {mover.combatant_id!r} has no grid position.")
        for source_id in source_ids:
            source = members.get(source_id)
            if source is None or source.state.position is None:
                continue
            before = footprint_distance_ft(
                mover.state.position,
                mover.state.template.size,
                source.state.position,
                source.state.template.size,
            )
            after = footprint_distance_ft(
                destination,
                mover.state.template.size,
                source.state.position,
                source.state.template.size,
            )
            if after < before:
                return True
        return False
    except Exception:
        logger.exception("Failed to evaluate frightened grid movement for %s.", mover.combatant_id)
        raise
