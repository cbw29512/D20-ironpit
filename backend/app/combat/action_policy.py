from __future__ import annotations

import logging

from app.combat.conditions import has_condition
from app.combat.recharge import get_recharge_state
from app.domain.models import CombatantState, SaveAction

logger = logging.getLogger(__name__)


def _recharge_available(actor: CombatantState, action: SaveAction) -> bool:
    if action.recharge is None:
        return True
    state = get_recharge_state(actor, action.id)
    return bool(state and state.available)


def _adds_new_condition(target: CombatantState, action: SaveAction) -> bool:
    condition_effects = [
        effect for effect in action.failure_effects
        if effect.effect_type == "condition"
    ]
    if not condition_effects:
        return False
    return any(
        not has_condition(target, effect.condition)
        for effect in condition_effects
    )


def select_standalone_save_action(
    actor: CombatantState,
    target: CombatantState,
    distance_ft: int,
) -> SaveAction | None:
    """Arena tactic: prefer a legal save action that can add a new condition."""
    try:
        if actor.template.multiattack is not None or not actor.action_available:
            return None
        for action in actor.template.save_actions:
            if action.action_cost != "action":
                continue
            if distance_ft > action.range_ft:
                continue
            if not _recharge_available(actor, action):
                continue
            if _adds_new_condition(target, action):
                return action
        return None
    except Exception as exc:
        logger.exception("Standalone action policy failed for %s.", actor.template.name)
        raise RuntimeError("Standalone action policy could not be evaluated.") from exc
