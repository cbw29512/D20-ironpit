from __future__ import annotations

from typing import NamedTuple

from app.combat.zero_hp import restore_hit_points
from app.domain.runtime import CombatantState


class RegenerationResult(NamedTuple):
    effect_id: str
    healed: int
    suppressed: bool


def resolve_regeneration(state: CombatantState) -> list[RegenerationResult]:
    """Resolve data-declared start-turn regeneration and clear prior-turn damage history."""
    damage_types = set(state.damage_types_since_last_turn)
    results: list[RegenerationResult] = []
    for effect in state.template.regeneration:
        suppressed = bool(damage_types.intersection(effect.suppressed_by_damage_types))
        eligible = not state.is_dead and (state.current_hp > 0 or not effect.requires_positive_hp)
        healed = restore_hit_points(state, effect.healing) if eligible and not suppressed else 0
        results.append(RegenerationResult(effect.id, healed, suppressed))
    state.damage_types_since_last_turn.clear()
    return results
