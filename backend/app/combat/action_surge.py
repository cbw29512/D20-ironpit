from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.domain.models import BattleEvent, CombatantState


def _resource(state: CombatantState):
    return next((item for item in state.resources if item.id == "action-surge"), None)


def action_surge_available(state: CombatantState, turn_key: str) -> bool:
    resource = _resource(state)
    return bool(
        resource is not None
        and resource.current_uses > 0
        and not state.action_available
        and not state.is_dead
        and not is_incapacitated(state)
        and state.feature_last_turn_keys.get("action-surge") != turn_key
    )


def use_action_surge(
    sequence: int,
    round_number: int,
    actor_id: str,
    state: CombatantState,
    turn_key: str,
) -> BattleEvent:
    """Grant Fighter's additional non-Magic Action once on this turn."""
    if not action_surge_available(state, turn_key):
        raise ValueError("Action Surge is not available.")
    resource = _resource(state)
    if resource is None:
        raise ValueError("Action Surge resource is missing.")
    resource.current_uses -= 1
    state.action_available = True
    state.feature_last_turn_keys["action-surge"] = turn_key
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=actor_id,
        actor_name=state.template.name,
        feature_id="action-surge",
        resource_remaining=resource.current_uses,
        animation="action-surge",
        description=f"{state.template.name} uses Action Surge and gains one additional Action.",
    )
