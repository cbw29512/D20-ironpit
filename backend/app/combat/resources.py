from __future__ import annotations

from app.combat.dice import DiceProvider
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
