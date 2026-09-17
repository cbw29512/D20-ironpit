from __future__ import annotations

from app.domain.models import CombatantState
from app.domain.modifiers import ModifierKind


def condition_is_immune(state: CombatantState, condition_id: str) -> bool:
    """Return static, feature-granted, and proximity-granted condition immunities."""
    if condition_id in state.template.condition_immunities:
        return True
    if any(
        item.kind is ModifierKind.CONDITION_IMMUNITY and item.condition_id == condition_id
        for item in state.active_modifiers
    ):
        return True
    if (
        state.template.progression_features.mindless_rage
        and "rage" in state.active_effect_ids
        and condition_id in {"charmed", "frightened"}
    ):
        return True
    if condition_id == "poisoned":
        active = {*state.active_effect_ids, *state.active_buff_effect_ids}
        return "petrified" in active or "protection-from-poison" in active
    return False
