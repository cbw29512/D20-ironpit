from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.area_targeting import AreaPlacement, legal_area_placements
from app.combat.offense_value import save_action_expected_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridDestinationPlan

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AreaMovementChoice:
    destination_plan: GridDestinationPlan
    placement: AreaPlacement
    expected_value: float


def best_area_destination(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    action,
    reachable: list[GridDestinationPlan],
) -> AreaMovementChoice | None:
    """Choose the reachable square whose best legal area placement has maximum damage value."""
    try:
        if action.area is None:
            raise ValueError(f"{action.id} does not define area geometry.")
        members = {
            member.combatant_id: member
            for member in [*setup.heroes, *setup.monsters]
        }
        candidates: list[AreaMovementChoice] = []
        for plan in reachable:
            placements = legal_area_placements(
                actor,
                setup,
                action.area,
                action.range_ft,
                actor_position=plan.destination,
            )
            for placement in placements:
                score = sum(
                    save_action_expected_damage(members[target_id], action)
                    for target_id in placement.target_ids
                )
                candidates.append(AreaMovementChoice(plan, placement, score))
        if not candidates:
            return None
        return min(candidates, key=lambda choice: (
            -choice.expected_value,
            -len(choice.placement.target_ids),
            choice.destination_plan.movement_cost_ft,
            choice.destination_plan.destination.x,
            choice.destination_plan.destination.y,
            choice.placement.target_ids,
        ))
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed reachable area-position scoring for %s.", actor.combatant_id)
        raise RuntimeError("Area movement choice could not be evaluated.") from exc
