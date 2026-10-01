from __future__ import annotations

import logging

from app.combat.resource_conversion import all_spell_slots_empty, conversion_available
from app.domain.models import CombatantState
from app.domain.resource_conversion import ResourceConversionAction

logger = logging.getLogger(__name__)


def _target_empty(state: CombatantState, action: ResourceConversionAction) -> bool:
    try:
        target = next(
            (item for item in state.resources if item.id == action.target_resource_id),
            None,
        )
        if target is None:
            raise ValueError(f"Resource conversion target {action.target_resource_id!r} is missing.")
        return target.current_uses == 0
    except Exception:
        logger.exception("Failed to inspect automatic conversion target for %s.", state.template.name)
        raise


def automatic_resource_conversion(
    state: CombatantState,
    turn_key: str | None = None,
) -> ResourceConversionAction | None:
    """Choose the highest-priority declared automatic conversion without mutating state."""
    try:
        candidates = [
            action
            for action in state.template.resource_conversion_actions
            if (
                (action.automation == "when-all-spell-slots-empty" and all_spell_slots_empty(state))
                or (action.automation == "when-target-empty" and _target_empty(state, action))
            )
            and conversion_available(state, action, turn_key)
        ]
        return sorted(candidates, key=lambda action: (-action.priority, action.id))[0] if candidates else None
    except Exception as exc:
        logger.exception("Failed to choose automatic resource conversion for %s.", state.template.name)
        raise RuntimeError("Automatic resource conversion could not be selected.") from exc
