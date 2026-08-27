from __future__ import annotations

import logging

from app.combat.condition_modifiers import has_zero_speed, is_incapacitated
from app.domain.models import CombatantState, CombatantTemplate, ResourceState

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
        incapacitated = is_incapacitated(state)
        state.action_available = not incapacitated
        state.bonus_action_available = not incapacitated
        state.reaction_available = not incapacitated
        state.action_surge_used_this_turn = False
        state.movement_remaining_ft = 0 if has_zero_speed(state) else state.template.speed_ft
    except Exception as exc:
        logger.exception("Failed to begin turn for %s.", state.template.name)
        raise RuntimeError("Turn state could not be initialized.") from exc
