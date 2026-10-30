from __future__ import annotations

import logging

from app.content.monster_movement_led_save_candidates import movement_led_save_candidates
from app.content.monster_source_grapple_lifecycle_candidates import grapple_lifecycle_save_candidates
from app.content.monster_source_grapple_save_candidates import grapple_save_candidates
from app.content.monster_source_repeat_save_candidates import repeat_condition_save_candidates
from app.content.monster_source_staged_save_candidates import staged_condition_save_candidates
from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.combatants import ResourceDefinition

logger = logging.getLogger(__name__)


def extended_save_candidates(
    monster: str,
    text: str,
    action_cost: ActionCost,
    speed: object,
) -> tuple[list[SaveCapabilityDefinition], list[ResourceDefinition]]:
    """Compile reusable save families that sit outside the core save grammar."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        resources: list[ResourceDefinition] = []

        staged, staged_resources = staged_condition_save_candidates(monster, text, action_cost)
        actions.extend(staged)
        resources.extend(staged_resources)
        actions.extend(repeat_condition_save_candidates(monster, text, action_cost))
        actions.extend(grapple_save_candidates(monster, text, action_cost))
        actions.extend(grapple_lifecycle_save_candidates(monster, text, action_cost))

        speed_parts = str(speed).split()
        abstract_range = int(speed_parts[0]) if speed_parts and speed_parts[0].isdigit() else 0
        moved, moved_resources = movement_led_save_candidates(
            monster,
            text,
            action_cost,
            abstract_range_ft=abstract_range,
        )
        actions.extend(moved)
        resources.extend(moved_resources)
        return actions, resources
    except Exception as exc:
        logger.exception("Failed extended save candidate compilation for %s.", monster)
        raise RuntimeError(f"Extended save candidates failed for {monster}.") from exc
