from __future__ import annotations

from app.combat.spellcasting import slot_spell_available
from app.domain.runtime import CombatantState, ResourceState


def available_spell_slots(
    state: CombatantState,
    minimum_level: int,
    turn_key: str,
) -> list[tuple[int, ResourceState]]:
    """Return usable slot resources at or above the spell's printed level."""
    if minimum_level < 1 or minimum_level > 9:
        raise ValueError("Slot spells require a printed level from 1 through 9.")
    if not slot_spell_available(state, turn_key):
        return []
    slots: list[tuple[int, ResourceState]] = []
    prefix = "spell-slot-"
    for resource in state.resources:
        if not resource.id.startswith(prefix) or resource.current_uses <= 0:
            continue
        try:
            level = int(resource.id[len(prefix):])
        except ValueError:
            continue
        if minimum_level <= level <= 9:
            slots.append((level, resource))
    return sorted(slots, key=lambda item: item[0])


def lowest_available_spell_slot(
    state: CombatantState,
    minimum_level: int,
    turn_key: str,
) -> tuple[int, ResourceState] | None:
    slots = available_spell_slots(state, minimum_level, turn_key)
    return slots[0] if slots else None
