from __future__ import annotations

from app.combat.spellcasting import slot_spell_available
from app.domain.runtime import CombatantState, ResourceState


def available_spell_slots(
    state: CombatantState,
    minimum_level: int,
    turn_key: str,
) -> list[tuple[int, ResourceState]]:
    """Return usable slots at the spell's printed level only.

    Iron Pit intentionally does not upcast spells. A spell can only consume a
    slot whose level exactly matches the spell's printed level.
    """
    if minimum_level < 1 or minimum_level > 9:
        raise ValueError("Slot spells require a printed level from 1 through 9.")
    if not slot_spell_available(state, turn_key):
        return []
    slot_id = f"spell-slot-{minimum_level}"
    return [
        (minimum_level, resource)
        for resource in state.resources
        if resource.id == slot_id and resource.current_uses > 0
    ]


def lowest_available_spell_slot(
    state: CombatantState,
    minimum_level: int,
    turn_key: str,
) -> tuple[int, ResourceState] | None:
    slots = available_spell_slots(state, minimum_level, turn_key)
    return slots[0] if slots else None
