from __future__ import annotations

from dataclasses import dataclass
import re

from app.content.monster_limited_use_source_audit import parse_limited_use_names
from app.content.monster_save_for_half_2024 import compile_save_for_half_actions
from app.domain.models import ResourceDefinition, SavingThrowAction
from app.domain.recharge import RechargeRule

_RECHARGE = re.compile(r"\(Recharge\s+(\d)(?:\s*[-–]\s*(\d))?\)$", re.I)


@dataclass(frozen=True)
class RechargeSaveBinding:
    source_name: str
    action: SavingThrowAction
    resource: ResourceDefinition
    recharge_rule: RechargeRule


def _action_name(source_name: str) -> str:
    heading = source_name.split(":", 1)[-1]
    return re.sub(r"\s*\([^)]*\)$", "", heading).strip()


def _minimum_roll(source_name: str) -> int | None:
    heading = source_name.split(":", 1)[-1].strip()
    match = _RECHARGE.search(heading)
    return int(match.group(1)) if match else None


def compile_recharge_save_bindings(row: dict[str, object]) -> list[RechargeSaveBinding]:
    """Bind source Recharge headings to already-compiled save-for-half actions."""
    expected = parse_limited_use_names(row)
    if not expected:
        return []
    compiled_actions = {
        action.name.casefold(): action
        for action in compile_save_for_half_actions(row)
        if action.resource_id is not None
    }
    bindings: list[RechargeSaveBinding] = []
    for source_name in expected:
        if not source_name.startswith("actions:"):
            continue
        minimum_roll = _minimum_roll(source_name)
        if minimum_roll is None:
            continue
        action_name = _action_name(source_name)
        action = compiled_actions.get(action_name.casefold())
        if action is None or action.resource_id is None:
            continue
        bindings.append(RechargeSaveBinding(
            source_name=source_name,
            action=action,
            resource=ResourceDefinition(
                id=action.resource_id,
                name=action.name,
                max_uses=1,
            ),
            recharge_rule=RechargeRule(
                resource_id=action.resource_id,
                minimum_roll=minimum_roll,
                die_size=6,
            ),
        ))
    return bindings


def recharge_save_coverage_matches(row: dict[str, object]) -> bool:
    """True only when every printed limited-use heading is an exact Recharge save binding."""
    expected = parse_limited_use_names(row)
    if not expected:
        return False
    bindings = compile_recharge_save_bindings(row)
    return sorted(binding.source_name for binding in bindings) == sorted(expected)
