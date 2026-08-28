from __future__ import annotations

import logging
from collections.abc import Iterable

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


def expire_attack_roll_effects_at_turn_start(
    active_actor: CombatantState,
    combatants: Iterable[CombatantState],
) -> None:
    """Expire effects whose RAW duration ends at the start of their source actor's turn."""
    try:
        source_actor_id = active_actor.template.id
        for state in combatants:
            state.attack_roll_effects = [
                effect
                for effect in state.attack_roll_effects
                if not (
                    effect.expires_at_start_of_source_turn
                    and effect.source_actor_id == source_actor_id
                )
            ]
    except Exception as exc:
        logger.exception(
            "Failed to expire turn-start effects for %s.", active_actor.template.name
        )
        raise RuntimeError("Turn-start effects could not be expired.") from exc


def begin_turn(state: CombatantState) -> None:
    try:
        state.action_available = True
        state.bonus_action_available = True
        state.movement_remaining_ft = state.template.speed_ft
    except Exception as exc:
        logger.exception("Failed to begin turn for %s.", state.template.name)
        raise RuntimeError("Turn state could not be initialized.") from exc
