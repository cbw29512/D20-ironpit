from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.events import AuditPhase, AuditStep, BattleEvent, DiceRoll, EventAudit
from app.domain.models import CombatantState, ResourceState, WeaponAttack


def find_resource(state: CombatantState, resource_id: str) -> ResourceState | None:
    return next((resource for resource in state.resources if resource.id == resource_id), None)


def action_resource_available(
    state: CombatantState,
    resource_id: str | None,
    resource_cost: int = 1,
) -> bool:
    if resource_id is None:
        return True
    resource = find_resource(state, resource_id)
    return resource is not None and resource.current_uses >= resource_cost


def spend_action_resource(
    state: CombatantState,
    resource_id: str | None,
    resource_cost: int = 1,
    *,
    action_id: str,
) -> None:
    if resource_id is None:
        return
    resource = find_resource(state, resource_id)
    if resource is None:
        raise ValueError(f"Action {action_id!r} references missing resource {resource_id!r}.")
    if resource.current_uses < resource_cost:
        raise ValueError(f"Action {action_id!r} does not have enough uses remaining.")
    resource.current_uses -= resource_cost


def attack_resource_available(state: CombatantState, attack: WeaponAttack) -> bool:
    return action_resource_available(state, attack.resource_id, attack.resource_cost)


def spend_attack_resource(state: CombatantState, attack: WeaponAttack) -> None:
    spend_action_resource(
        state,
        attack.resource_id,
        attack.resource_cost,
        action_id=attack.id,
    )


def recharge_start_of_turn(state: CombatantState, dice: DiceProvider) -> list[tuple[str, int, bool]]:
    """Roll each depleted Recharge resource once at the start of its owner's turn."""
    results: list[tuple[str, int, bool]] = []
    for resource in state.resources:
        threshold = resource.recharge_d6_min
        if threshold is None or resource.current_uses >= resource.max_uses:
            continue
        roll = dice.roll(6)
        restored = roll >= threshold
        if restored:
            resource.current_uses = resource.max_uses
        results.append((resource.id, roll, restored))
    return results


def recharge_start_events(
    sequence: int,
    round_number: int,
    state: CombatantState,
    actor_id: str,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for resource_id, roll, restored in recharge_start_of_turn(state, dice):
        resource = find_resource(state, resource_id)
        if resource is None or resource.recharge_d6_min is None:
            raise ValueError(f"Recharge result references missing resource {resource_id!r}.")
        threshold = resource.recharge_d6_min
        requirement = f"{threshold}–6" if threshold < 6 else "6"
        result_text = (
            f"Recharge condition met: rolled {roll}, needs {requirement}. {resource.name} is restored."
            if restored
            else f"Recharge condition not met: rolled {roll}, needs {requirement}. {resource.name} remains unavailable."
        )
        events.append(BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor_id,
            actor_name=state.template.name,
            feature_id=f"recharge:{resource_id}",
            attack_roll=DiceRoll(
                notation="1d6", rolls=[roll], selected_roll=roll, modifier=0, total=roll,
            ),
            resource_remaining=resource.current_uses,
            animation="resource",
            description=f"{state.template.name}: {result_text}",
            audit=EventAudit(steps=[
                AuditStep(
                    phase=AuditPhase.ROLL,
                    kind="roll",
                    label=f"Recharge check: rolled {roll}; needs {requirement}; {'met' if restored else 'not met'}",
                ),
                AuditStep(
                    phase=AuditPhase.RESOURCE_CHANGE,
                    kind="resource",
                    label=f"{resource.name}: {resource.current_uses}/{resource.max_uses}",
                ),
            ]),
        ))
        sequence += 1
    return events, sequence
