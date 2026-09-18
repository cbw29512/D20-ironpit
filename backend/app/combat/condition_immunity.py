from __future__ import annotations

from app.combat.defensive_modifier_rules import condition_immunity_modifier_applies
from app.domain.models import CombatantState, CombatantTemplate


def condition_is_immune(
    state: CombatantState,
    condition_id: str,
    source: CombatantTemplate | None = None,
) -> bool:
    """Return static and runtime condition immunities, including source-typed wards."""
    if condition_id in state.template.condition_immunities:
        return True
    if any(
        condition_immunity_modifier_applies(item, condition_id, source)
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
