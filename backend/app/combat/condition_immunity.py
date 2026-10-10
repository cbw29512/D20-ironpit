from __future__ import annotations

from app.combat.debuff_counters import debuff_is_countered
from app.combat.defensive_modifier_rules import condition_immunity_modifier_applies
from app.combat.flight_ground_immunity import flying_counters_ground_contact
from app.domain.models import CombatantState, CombatantTemplate


def condition_is_immune(
    state: CombatantState,
    condition_id: str,
    source: CombatantTemplate | None = None,
    *,
    source_is_magical: bool = False,
    ground_contact: bool = False,
    actor=None,
    setup=None,
) -> bool:
    """Return static and runtime condition immunities, including source-typed wards.

    ``source_is_magical`` is explicit source metadata. It must never be inferred
    from a display name: callers resolving a spell or other magical effect own
    that fact. This keeps magical-only prevention distinct from blanket
    condition immunity and lets nonmagical sources continue to function.
    """
    if actor is not None and setup is not None and actor.state is state:
        from app.combat.steadfast_condition_immunity import steadfast_frightened_immunity
        if steadfast_frightened_immunity(actor, setup, condition_id):
            return True
    if condition_id in state.template.condition_immunities:
        return True
    if flying_counters_ground_contact(state, ground_contact=ground_contact):
        return True
    if debuff_is_countered(
        state,
        condition_id,
        source_is_magical=source_is_magical,
    ):
        return True
    if any(
        condition_immunity_modifier_applies(item, state, condition_id, source)
        for item in state.active_modifiers
    ):
        return True
    if (
        state.template.ruleset != "2014"
        and state.template.progression_features.mindless_rage
        and "rage" in state.active_effect_ids
        and condition_id in {"charmed", "frightened"}
    ):
        return True
    if condition_id == "poisoned":
        return "petrified" in state.active_effect_ids
    return False
