from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.models import BattleEvent, CombatantState, DiceRoll, RollMode


def resource_state(state: CombatantState, resource_id: str):
    return next((item for item in state.resources if item.id == resource_id), None)


def resource_definition(state: CombatantState, resource_id: str):
    return next((item for item in state.template.resources if item.id == resource_id), None)


def resource_available(state: CombatantState, resource_id: str | None, cost: int = 1) -> bool:
    if resource_id is None:
        return True
    resource = resource_state(state, resource_id)
    return resource is not None and resource.current_uses >= cost


def spend_resource(state: CombatantState, resource_id: str | None, cost: int = 1) -> int | None:
    if resource_id is None:
        return None
    resource = resource_state(state, resource_id)
    if resource is None or resource.current_uses < cost:
        raise ValueError(f"Resource {resource_id!r} is unavailable.")
    resource.current_uses -= cost
    return resource.current_uses


def action_resource_available(state: CombatantState, action) -> bool:
    return resource_available(state, getattr(action, "resource_id", None), getattr(action, "resource_cost", 1))


def spend_action_resource(state: CombatantState, action) -> int | None:
    return spend_resource(state, getattr(action, "resource_id", None), getattr(action, "resource_cost", 1))


def resolve_start_turn_recharges(
    sequence: int,
    round_number: int,
    actor_id: str,
    state: CombatantState,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Roll only expended Recharge resources at the start of their owner's turn."""
    events: list[BattleEvent] = []
    for definition in state.template.resources:
        rule = definition.recharge
        current = resource_state(state, definition.id)
        if rule is None or current is None or current.current_uses >= current.max_uses:
            continue
        rolled = dice.roll(rule.die_size)
        recovered = rolled >= rule.minimum_roll
        if recovered:
            current.current_uses = current.max_uses
        roll = DiceRoll(
            notation=f"1d{rule.die_size}", rolls=[rolled], selected_roll=rolled,
            modifier=0, mode=RollMode.NORMAL, total=rolled,
        )
        threshold = str(rule.minimum_roll) if rule.minimum_roll == rule.die_size else f"{rule.minimum_roll}-{rule.die_size}"
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=actor_id, actor_name=state.template.name, feature_id=definition.id,
            resource_roll=roll, resource_remaining=current.current_uses,
            animation="recharge",
            description=(f"{state.template.name} rolls {rolled} for {definition.name} (Recharge {threshold}): "
                         f"{'RECHARGED' if recovered else 'not recharged'}."),
        ))
        sequence += 1
    return events, sequence
