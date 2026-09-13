from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def describe_save_outcome(
    *, target_name: str, actor_name: str, action_name: str, dc: int,
    save_ability: str, succeeded: bool, movement_ft: int,
    damage_outcome: str | None, applied_conditions: list[str],
) -> str:
    try:
        outcome = "SUCCEEDS" if succeeded else "FAILS"
        description = (
            f"{target_name} {outcome} a DC {dc} {save_ability.title()} save "
            f"against {actor_name}'s {action_name}."
        )
        if movement_ft:
            description += f" {target_name} is pushed {movement_ft} ft. straight away."
        if damage_outcome == "undead_fortitude":
            description += f" {target_name} succeeds on Undead Fortitude and remains at 1 HP."
        for condition in applied_conditions:
            if condition == "grappled":
                description += f" {target_name} is Grappled."
            elif condition == "restrained":
                description += f" {target_name} is Restrained while Grappled."
            else:
                description += f" {target_name} is {condition.title()}."
        return description
    except Exception as exc:
        logger.exception("Failed to describe saving-throw outcome for %s.", target_name)
        raise RuntimeError("Saving-throw outcome description failed.") from exc
