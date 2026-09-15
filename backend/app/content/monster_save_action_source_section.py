from __future__ import annotations

import re

_ACTION_COST_FIELD = {
    "action": "actions",
    "bonus_action": "bonusActions",
    "reaction": "reactions",
}


def save_action_source(row: dict[str, object], action_cost: str) -> str:
    """Return normalized SRD text for the action-economy section that owns a save."""
    try:
        field = _ACTION_COST_FIELD.get(action_cost)
        return re.sub(r"\s+", " ", str(row.get(field, ""))).strip().lower() if field else ""
    except Exception as exc:
        raise RuntimeError(f"Unable to resolve save source section for {action_cost!r}.") from exc
