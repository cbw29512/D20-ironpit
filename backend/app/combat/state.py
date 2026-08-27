from __future__ import annotations

import logging

from app.domain.models import CombatantState, CombatantTemplate, ConditionType, ResourceState

logger = logging.getLogger(__name__)


def build_combatant_state(
    template: CombatantTemplate,
    instance_id: str | None = None,
) -> CombatantState:
    try:
        return CombatantState(
            template=template,
            instance_id=instance_id or template.id,
            current_hp=template.max_hp,
            movement_remaining_ft=0,
            resources=[
                ResourceState(
                    id=resource.id,
                    name=resource.name,
                    current_uses=resource.max_uses,
                    max_uses=resource.max_uses,
                )
                for resource in template.resources
            ],
        )
    except Exception as exc:
        logger.exception("Failed to build runtime state for %s.", template.name)
        raise RuntimeError("Combatant state could not be created.") from exc


def begin_turn(state: CombatantState) -> None:
    try:
        state.action_available = True
        state.bonus_action_available = True
        state.action_surge_used_this_turn = False
        grappled = any(item.condition is ConditionType.GRAPPLED for item in state.conditions)
        state.movement_remaining_ft = 0 if grappled else state.template.speed_ft
    except Exception as exc:
        logger.exception("Failed to begin turn for %s.", state.template.name)
        raise RuntimeError("Turn state could not be initialized.") from exc
