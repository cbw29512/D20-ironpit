from __future__ import annotations

from app.domain.models import CombatantState


def condition_is_immune(state: CombatantState, condition_id: str) -> bool:
    """Return static and condition-granted 2024 condition immunities."""
    if condition_id in state.template.condition_immunities:
        return True
    return condition_id == "poisoned" and "petrified" in state.active_effect_ids
