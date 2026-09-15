from __future__ import annotations

from typing import Any

from app.combat.spellcasting import mark_slot_spell_cast
from app.domain.encounters import EncounterCombatant


def spend_spell_cast_resource(caster: EncounterCombatant, choice: Any, turn_key: str) -> int | None:
    """Spend the resource selected by spell policy: slot, innate use, or none for at-will."""
    resource_id = choice.resource_id
    if resource_id is None:
        return None
    resource = next((item for item in caster.state.resources if item.id == resource_id), None)
    if resource is None or resource.current_uses < 1:
        raise ValueError(f"No {resource_id} resource remains.")
    if resource_id.startswith("spell-slot-"):
        mark_slot_spell_cast(caster.state, turn_key)
    resource.current_uses -= 1
    return resource.current_uses


def spell_cast_resource_text(choice: Any) -> str:
    if choice.resource_id is None:
        return "cantrip" if choice.slot_level == 0 else "at-will spell"
    if choice.resource_id.startswith("innate-"):
        return "innate spell use"
    return f"level {choice.slot_level} slot"
