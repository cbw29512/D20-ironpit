from __future__ import annotations

import logging

from app.combat.grid_path_execution import execute_grid_path
from app.combat.grid_pathing import plan_movement_toward
from app.combat.opportunity_attacks import MovementSource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def move_toward_on_grid(
    sequence: int,
    round_number: int,
    mover: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    desired_distance_ft: int,
    dice,
    *,
    movement_source: MovementSource = "speed",
    disengaged: bool = False,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int, BattleEvent | None]:
    """Plan an approach route, then execute it through the universal path engine."""
    try:
        if setup.map_definition is None or mover.state.position is None or target.state.position is None:
            raise ValueError("Grid movement requires an authoritative map and grid positions.")
        plan = plan_movement_toward(
            setup.map_definition,
            mover,
            target,
            [*setup.heroes, *setup.monsters],
            desired_distance_ft,
            mover.state.movement_remaining_ft,
        )
        if not plan.path:
            return [], sequence, None
        return execute_grid_path(
            sequence,
            round_number,
            mover,
            setup,
            plan.path,
            dice,
            target=target,
            movement_source=movement_source,
            disengaged=disengaged,
            turn_key=turn_key,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Grid movement execution failed for %s.", mover.combatant_id)
        raise RuntimeError("Grid movement could not be resolved.") from exc
