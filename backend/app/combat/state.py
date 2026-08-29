from __future__ import annotations

import logging

from app.combat.conditions import DODGE_EFFECT_ID, stand_from_prone
from app.combat.grapple import speed_is_zero
from app.domain.models import CombatantState, CombatantTemplate, ResourceState

logger = logging.getLogger(__name__)


def build_combatant_state(template: CombatantTemplate) -> CombatantState:
    try:
        return CombatantState(
            template=template,
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
        state.movement_remaining_ft = 0 if speed_is_zero(state) else state.template.speed_ft
        if DODGE_EFFECT_ID in state.active_effect_ids:
            state.active_effect_ids.remove(DODGE_EFFECT_ID)
        stand_from_prone(state)
    except Exception as exc:
        logger.exception("Failed to begin turn for %s.", state.template.name)
        raise RuntimeError("Turn state could not be initialized.") from exc
