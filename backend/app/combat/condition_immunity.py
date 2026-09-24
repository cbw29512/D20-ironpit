from __future__ import annotations

from app.combat.defensive_modifier_rules import condition_immunity_modifier_applies
from app.domain.models import CombatantState, CombatantTemplate


def condition_is_immune(
    state: CombatantState,
    condition_id: str,
    source: CombatantTemplate | None = None,
    *,
    source_is_magical: bool = False,
) -> bool:
    """Return static and runtime condition immunities, including source-typed wards.

    ``source_is_magical`` is explicit source metadata. It must never be inferred
    from a display name: callers resolving a spell or other magical effect own
    that fact. This keeps magical-only prevention distinct from blanket
    condition immunity and lets nonmagical sources continue to function.
    """
    if condition_id in state.template.condition_immunities:
        return True
    if source_is_magical and any(
        condition_id in effect.owned_magical_condition_immunities
        for effect in state.timed_effects
    ):
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
