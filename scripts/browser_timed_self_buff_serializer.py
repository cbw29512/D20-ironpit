from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def timed_self_buff_row(action: Any) -> dict[str, Any]:
    try:
        row = {
            "id": action.id,
            "name": action.name,
            "actionCost": action.action_cost,
            "resourceId": action.resource_id,
            "resourceCost": action.resource_cost,
            "durationRounds": action.duration_rounds,
            "conditionIds": list(action.condition_ids),
            "magicalEffect": action.magical_effect,
            "concentration": action.concentration,
            "endsOnOwnerAttack": action.ends_on_owner_attack,
            "endsOnOwnerSpellCast": action.ends_on_owner_spell_cast,
            "priority": action.priority,
            "animation": action.animation,
        }
        return row
    except Exception as exc:
        logger.exception("Failed to serialize timed self buff %s.", getattr(action, "id", "<unknown>"))
        raise RuntimeError("Timed self buff could not be serialized.") from exc
