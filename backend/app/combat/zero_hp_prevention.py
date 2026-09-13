from __future__ import annotations

from app.domain.models import CombatantState


def use_zero_hp_prevention(state: CombatantState, incoming_damage: int) -> bool:
    profile = state.template.zero_hp_prevention
    if profile is None or incoming_damage > profile.max_trigger_damage:
        return False
    resource = next((item for item in state.resources if item.id == profile.resource_id), None)
    if resource is None or resource.current_uses <= 0:
        return False
    resource.current_uses -= 1
    state.current_hp = profile.resulting_hp
    state.is_alive = True
    state.is_dead = False
    state.is_unconscious = False
    state.is_stable = False
    return True
