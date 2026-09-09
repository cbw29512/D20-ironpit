from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.combat.grid_pathing import plan_movement_toward
from app.combat.grid_pathing_support import movement_step_cost_ft
from app.combat.grid_reaction_movement_support import approaches_fear_source, distance_to_position
from app.combat.grapple import speed_is_zero
from app.combat.opportunity_attacks import MovementSource, resolve_opportunity_attack
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
    """Execute a planned grid route one square at a time with RAW reaction windows."""
    try:
        if setup.map_definition is None or mover.state.position is None or target.state.position is None:
            raise ValueError("Grid movement requires an authoritative map and grid positions.")
        members = [*setup.heroes, *setup.monsters]
        plan = plan_movement_toward(
            setup.map_definition,
            mover,
            target,
            members,
            desired_distance_ft,
            mover.state.movement_remaining_ft,
        )
        if not plan.path:
            return [], sequence, None

        events: list[BattleEvent] = []
        last_movement: BattleEvent | None = None
        reactors = setup.monsters if mover.side == "heroes" else setup.heroes

        for destination in plan.path:
            if approaches_fear_source(mover, destination, setup):
                break
            before_position = mover.state.position.model_copy(deep=True)
            step_cost = movement_step_cost_ft(setup.map_definition, mover, destination, members)
            if step_cost is None or step_cost > mover.state.movement_remaining_ft:
                break
            was_prone = "prone" in mover.state.active_effect_ids
            for reactor in reactors:
                if reactor.state.position is None:
                    continue
                reaction = resolve_opportunity_attack(
                    sequence,
                    round_number,
                    reactor,
                    mover,
                    setup,
                    distance_to_position(reactor, mover, before_position),
                    distance_to_position(reactor, mover, destination),
                    movement_source,
                    dice,
                    disengaged=disengaged,
                    turn_key=turn_key,
                )
                if reaction is None:
                    continue
                events.append(reaction)
                sequence += 1
                newly_prone = not was_prone and "prone" in mover.state.active_effect_ids
                if mover.state.is_dead or mover.state.is_unconscious or speed_is_zero(mover.state) or newly_prone:
                    return events, sequence, last_movement

            before_distance = footprint_distance_ft(
                before_position,
                mover.state.template.size,
                target.state.position,
                target.state.template.size,
            )
            mover.state.position = destination.model_copy(deep=True)
            mover.state.movement_remaining_ft -= step_cost
            after_distance = footprint_distance_ft(
                mover.state.position,
                mover.state.template.size,
                target.state.position,
                target.state.template.size,
            )
            last_movement = BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="movement",
                actor_id=mover.combatant_id,
                actor_name=mover.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                distance_before_ft=before_distance,
                distance_after_ft=after_distance,
                movement_ft=setup.map_definition.cell_size_ft,
                movement_cost_ft=step_cost,
                grid_position_before=before_position,
                grid_position_after=mover.state.position.model_copy(deep=True),
                grid_path=[mover.state.position.model_copy(deep=True)],
                animation="advance",
                description=(
                    f"{mover.state.template.name} moves 5 feet."
                    if step_cost == 5
                    else f"{mover.state.template.name} moves 5 feet, spending {step_cost} feet of movement."
                ),
            )
            events.append(last_movement)
            sequence += 1
            if after_distance <= desired_distance_ft or mover.state.movement_remaining_ft <= 0:
                break
        return events, sequence, last_movement
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Grid movement execution failed for %s.", mover.combatant_id)
        raise RuntimeError("Grid movement could not be resolved.") from exc
