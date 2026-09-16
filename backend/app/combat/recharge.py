from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.dice import DiceProvider
from app.domain.runtime import CombatantState, ResourceState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RechargeCheck:
    resource_id: str
    roll: int
    minimum_roll: int
    restored: bool
    resource_remaining: int


def _resource(state: CombatantState, resource_id: str) -> ResourceState:
    try:
        return next(resource for resource in state.resources if resource.id == resource_id)
    except StopIteration as exc:
        logger.error("Recharge resource %s is missing on %s.", resource_id, state.template.name)
        raise ValueError(f"Recharge resource '{resource_id}' is not defined.") from exc


def resolve_recharge_checks(state: CombatantState, dice: DiceProvider) -> list[RechargeCheck]:
    """Roll only expended Recharge resources; successful checks restore availability."""
    checks: list[RechargeCheck] = []
    try:
        for rule in state.template.recharge_rules:
            resource = _resource(state, rule.resource_id)
            if resource.current_uses > 0:
                continue
            roll = dice.roll(rule.die_size)
            restored = roll >= rule.minimum_roll
            if restored:
                resource.current_uses = resource.max_uses
            checks.append(RechargeCheck(
                resource_id=resource.id,
                roll=roll,
                minimum_roll=rule.minimum_roll,
                restored=restored,
                resource_remaining=resource.current_uses,
            ))
        return checks
    except Exception as exc:
        logger.exception("Recharge resolution failed for %s.", state.template.name)
        if isinstance(exc, ValueError):
            raise
        raise RuntimeError("Recharge checks could not be resolved.") from exc
