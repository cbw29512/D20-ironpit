from __future__ import annotations

import logging
from typing import Any, NamedTuple

from app.combat.dice import DiceProvider
from app.domain.events import AuditPhase, AuditStep, BattleEvent, EventAudit
from app.domain.runtime import CombatantState, ResourceState

logger = logging.getLogger(__name__)


class RechargeResult(NamedTuple):
    resource_id: str
    roll: int
    recharged: bool


def resource_state(state: CombatantState, resource_id: str) -> ResourceState | None:
    return next((item for item in state.resources if item.id == resource_id), None)


def can_spend_resource(state: CombatantState, resource_id: str | None, cost: int = 1) -> bool:
    if resource_id is None:
        return True
    resource = resource_state(state, resource_id)
    return resource is not None and resource.current_uses >= cost


def can_use_action_resource(state: CombatantState, action: Any) -> bool:
    return can_spend_resource(
        state,
        getattr(action, "resource_id", None),
        getattr(action, "resource_cost", 1),
    )


def spend_action_resource(state: CombatantState, action: Any) -> int | None:
    resource_id = getattr(action, "resource_id", None)
    if resource_id is None:
        return None
    cost = getattr(action, "resource_cost", 1)
    resource = resource_state(state, resource_id)
    if resource is None or resource.current_uses < cost:
        raise ValueError(f"Resource {resource_id} is unavailable for {getattr(action, 'id', 'action')}.")
    resource.current_uses -= cost
    return resource.current_uses


def refresh_recharge_resources(state: CombatantState, dice: DiceProvider) -> list[RechargeResult]:
    """At monster turn start, roll only depleted abilities that declare Recharge."""
    if state.template.kind != "monster":
        return []
    recharge_definitions = {
        item.id: item
        for item in state.template.resources
        if item.recharge_minimum is not None
    }
    if not recharge_definitions:
        return []
    results: list[RechargeResult] = []
    for resource in state.resources:
        definition = recharge_definitions.get(resource.id)
        if definition is None or resource.current_uses >= resource.max_uses:
            continue
        roll = dice.roll(definition.recharge_die_size)
        recharged = roll >= definition.recharge_minimum
        if recharged:
            resource.current_uses = resource.max_uses
        results.append(RechargeResult(resource.id, roll, recharged))
    return results


def build_recharge_events(
    state: CombatantState,
    actor_id: str,
    round_number: int,
    sequence: int,
    results: list[RechargeResult],
) -> tuple[list[BattleEvent], int]:
    """Convert start-turn Recharge state changes into audit-grade universal events."""
    try:
        definitions = {item.id: item for item in state.template.resources}
        events: list[BattleEvent] = []
        for result in results:
            definition = definitions[result.resource_id]
            runtime = resource_state(state, result.resource_id)
            remaining = runtime.current_uses if runtime is not None else 0
            threshold = definition.recharge_minimum
            outcome = f"recharged to {remaining}" if result.recharged else "did not recharge"
            roll_label = f"Recharge d{definition.recharge_die_size}: {result.roll} vs {threshold}+"
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=actor_id,
                actor_name=state.template.name,
                feature_id=result.resource_id,
                resource_remaining=remaining,
                animation="resource",
                description=f"{state.template.name} rolls {definition.name} {roll_label}; {outcome}.",
                audit=EventAudit(steps=[
                    AuditStep(phase=AuditPhase.ROLL, kind="roll", label=roll_label),
                    AuditStep(
                        phase=AuditPhase.RESOURCE_CHANGE,
                        kind="resource",
                        label=f"{definition.name}: {outcome}",
                    ),
                ]),
            ))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Failed to build Recharge audit events for %s.", state.template.name)
        raise RuntimeError("Recharge audit events could not be created.") from exc
