from __future__ import annotations

from app.combat.spellcasting import slot_spell_available
from app.domain.runtime import CombatantState, ResourceState


def _spell_slot_level(resource: ResourceState) -> int | None:
    prefix = "spell-slot-"
    if not resource.id.startswith(prefix):
        return None
    try:
        level = int(resource.id[len(prefix):])
    except ValueError:
        return None
    return level if 1 <= level <= 9 else None


def available_spell_slots(
    state: CombatantState,
    minimum_level: int,
    turn_key: str,
    *,
    allow_higher: bool = False,
) -> list[tuple[int, ResourceState]]:
    """Return legal spell slots for a certified spell action.

    Exact-level casting is the default. Higher slots are exposed only when the
    caller explicitly represents a certified upcast mechanic on that action.
    """
    if minimum_level < 1 or minimum_level > 9:
        raise ValueError("Slot spells require a printed level from 1 through 9.")
    if not slot_spell_available(state, turn_key):
        return []

    slots: list[tuple[int, ResourceState]] = []
    for resource in state.resources:
        if resource.current_uses < 1:
            continue
        level = _spell_slot_level(resource)
        if level is None:
            continue
        if level == minimum_level or (allow_higher and level > minimum_level):
            slots.append((level, resource))
    return sorted(slots, key=lambda item: item[0])


def lowest_available_spell_slot(
    state: CombatantState,
    minimum_level: int,
    turn_key: str,
    *,
    allow_higher: bool = False,
) -> tuple[int, ResourceState] | None:
    slots = available_spell_slots(state, minimum_level, turn_key, allow_higher=allow_higher)
    return slots[0] if slots else None
