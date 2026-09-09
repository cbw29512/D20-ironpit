from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.conditions import DODGE_EFFECT_ID, stand_from_prone
from app.combat.grapple import speed_is_zero
from app.combat.heroic_inspiration import grant_heroic_warrior_inspiration
from app.combat.modifier_stack import effective_speed
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
                    id=r.id,
                    name=r.name,
                    current_uses=r.max_uses,
                    max_uses=r.max_uses,
                    recharge_d6_min=r.recharge_d6_min,
                )
                for r in template.resources
            ],
        )
    except Exception as exc:
        logger.exception("Failed to build runtime state for %s.", template.name)
        raise RuntimeError("Combatant state could not be created.") from exc


def refresh_reaction(state: CombatantState) -> None:
    """A creature regains its Reaction at the start of its turn, even if Incapacitated."""
    state.reaction_available = True


def refresh_start_of_turn(state: CombatantState) -> None:
    refresh_reaction(state)
    grant_heroic_warrior_inspiration(state)


def terminate_turn(state: CombatantState, reason: str) -> None:
    """End voluntary activity for the current turn without consuming the creature's Reaction."""
    state.turn_terminated = True
    state.turn_termination_reason = reason
    state.action_available = False
    state.bonus_action_available = False
    state.movement_remaining_ft = 0


def begin_turn(state: CombatantState) -> None:
    try:
        state.turn_terminated = False
        state.turn_termination_reason = None
        incapacitated = is_incapacitated(state)
        state.action_available = not incapacitated
        state.bonus_action_available = not incapacitated
        refresh_start_of_turn(state)
        speed = effective_speed(state)
        state.movement_remaining_ft = 0 if speed_is_zero(state) else speed
        if DODGE_EFFECT_ID in state.active_effect_ids:
            state.active_effect_ids.remove(DODGE_EFFECT_ID)
        stand_from_prone(state)
    except Exception as exc:
        logger.exception("Failed to begin turn for %s.", state.template.name)
        raise RuntimeError("Turn state could not be initialized.") from exc