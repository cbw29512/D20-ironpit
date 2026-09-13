from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def refresh_legendary_actions(state: CombatantState) -> None:
    """Refresh all expended uses and per-option lockouts at the owner's turn start."""
    try:
        pool = state.template.legendary_actions
        if pool is None:
            state.legendary_action_uses_remaining = 0
            state.legendary_action_locked_option_ids.clear()
            return
        state.legendary_action_uses_remaining = pool.max_uses
        state.legendary_action_locked_option_ids.clear()
    except Exception:
        logger.exception("Failed to refresh legendary actions for %s.", state.template.name)
        raise


def can_spend_legendary_action(
    state: CombatantState,
    option_id: str,
    *,
    owner_combatant_id: str,
    completed_turn_combatant_id: str,
) -> bool:
    """Check the universal 2024 timing/economy gate without resolving the option body."""
    try:
        pool = state.template.legendary_actions
        if pool is None or owner_combatant_id == completed_turn_combatant_id:
            return False
        if state.is_dead or state.is_unconscious or is_incapacitated(state):
            return False
        option = next((item for item in pool.options if item.id == option_id), None)
        if option is None or option.id in state.legendary_action_locked_option_ids:
            return False
        return state.legendary_action_uses_remaining >= option.cost
    except Exception:
        logger.exception("Failed legendary-action legality check for %s.", state.template.name)
        raise


def spend_legendary_action(state: CombatantState, option_id: str) -> None:
    """Spend only the immutable option's declared cost; option effects resolve elsewhere."""
    try:
        pool = state.template.legendary_actions
        if pool is None:
            raise ValueError("Combatant has no legendary action pool.")
        option = next((item for item in pool.options if item.id == option_id), None)
        if option is None:
            raise ValueError(f"Unknown legendary action option: {option_id}")
        if state.legendary_action_uses_remaining < option.cost:
            raise ValueError("Insufficient legendary action uses.")
        state.legendary_action_uses_remaining -= option.cost
        if option.once_until_owner_turn:
            state.legendary_action_locked_option_ids.append(option.id)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to spend legendary action for %s.", state.template.name)
        raise RuntimeError("Legendary action use could not be spent.") from exc
