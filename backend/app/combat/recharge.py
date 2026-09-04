from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.dice import DiceProvider
from app.combat.resource_pool import get_resource, restore_resource
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RechargeRule:
    """Reusable Recharge X-Y rule for one limited-use runtime resource."""

    resource_id: str
    minimum: int
    maximum: int = 6
    die_size: int = 6

    def __post_init__(self) -> None:
        if not self.resource_id:
            raise ValueError("Recharge requires a resource ID.")
        if self.die_size < 2:
            raise ValueError("Recharge die must have at least two sides.")
        if not 1 <= self.minimum <= self.maximum <= self.die_size:
            raise ValueError("Recharge range must fit within the recharge die.")


@dataclass(frozen=True)
class RechargeResult:
    roll: int | None
    recharged: bool
    resource_remaining: int


def resolve_recharge_start_of_turn(
    state: CombatantState,
    rule: RechargeRule,
    dice: DiceProvider,
) -> RechargeResult:
    """Roll Recharge only when the referenced ability is currently spent."""
    try:
        item = get_resource(state, rule.resource_id)
        if item is None:
            raise ValueError(f"Recharge resource {rule.resource_id!r} is missing.")
        if item.current_uses >= item.max_uses:
            return RechargeResult(None, False, item.current_uses)
        roll = dice.roll(rule.die_size)
        recharged = rule.minimum <= roll <= rule.maximum
        if recharged:
            item = restore_resource(state, rule.resource_id)
        return RechargeResult(roll, recharged, item.current_uses)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Recharge failed for %s resource %s.", state.template.name, rule.resource_id)
        raise RuntimeError("Recharge could not be resolved.") from exc
