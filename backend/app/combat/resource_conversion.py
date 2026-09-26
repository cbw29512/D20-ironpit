from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.resources import gain_resource, resource_available, spend_resource
from app.domain.events import BattleEvent
from app.domain.models import CombatantState
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)


def conversion_available(state: CombatantState, action: ResourceConversionAction) -> bool:
    try:
        if not is_available(state, action.action_cost):
            return False
        if not resource_available(state, action.source_resource_id, action.source_cost):
            return False
        target = next((item for item in state.resources if item.id == action.target_resource_id), None)
        if target is None:
            raise ValueError(f"Resource conversion target {action.target_resource_id!r} is missing.")
        return action.target_allows_overflow or target.current_uses < target.max_uses
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to evaluate resource conversion %s for %s.", action.id, state.template.name)
        raise RuntimeError("Resource conversion availability could not be resolved.") from exc


def resolve_resource_conversion(
    state: CombatantState,
    action: ResourceConversionAction,
    *,
    sequence: int,
    round_number: int,
    actor_id: str,
) -> BattleEvent:
    try:
        if not conversion_available(state, action):
            raise ValueError(f"Resource conversion {action.id!r} is unavailable.")
        spend(state, action.action_cost)
        source_remaining = spend_resource(state, action.source_resource_id, action.source_cost)
        target_remaining = gain_resource(
            state,
            action.target_resource_id,
            action.target_gain,
            allow_overflow=action.target_allows_overflow,
        )
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor_id,
            actor_name=state.template.name,
            feature_id=action.id,
            resource_remaining=source_remaining,
            animation="resource-conversion",
            description=(
                f"{state.template.name} uses {action.name}, spending {action.source_cost} "
                f"{action.source_resource_id} and gaining {action.target_gain} "
                f"{action.target_resource_id} ({target_remaining} available)."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve resource conversion %s for %s.", action.id, state.template.name)
        raise RuntimeError("Resource conversion could not be resolved.") from exc
