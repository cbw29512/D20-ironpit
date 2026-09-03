from __future__ import annotations

from app.domain.models import CombatantState


def condition_is_immune(state: CombatantState, condition_id: str) -> bool:
    """Return static and condition-granted 2024 condition immunities plus Iron Pit protections."""
    if condition_id in state.template.condition_immunities:
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
