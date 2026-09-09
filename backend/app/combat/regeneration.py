from __future__ import annotations

from typing import NamedTuple

from app.combat.hit_points import effective_max_hp
from app.domain.runtime import CombatantState


class RegenerationResult(NamedTuple):
    effect_id: str
    healed: int
    suppressed: bool


def defers_death_at_zero(state: CombatantState) -> bool:
    return any(not effect.requires_positive_hp for effect in state.template.regeneration)


def _restore(state: CombatantState, amount: int) -> int:
    before = state.current_hp
    state.current_hp = min(effective_max_hp(state), before + amount)
    healed = state.current_hp - before
    if healed > 0:
        state.is_alive = True
        state.is_dead = False
        state.is_unconscious = False
        state.is_stable = False
        state.death_save_successes = 0
        state.death_save_failures = 0
    return healed


def _die_at_zero(state: CombatantState) -> None:
    state.current_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False


def resolve_regeneration(state: CombatantState) -> list[RegenerationResult]:
    """Resolve data-declared start-turn regeneration and its zero-HP death gate."""
    damage_types = set(state.damage_types_since_last_turn)
    started_at_zero = state.current_hp == 0 and defers_death_at_zero(state)
    results: list[RegenerationResult] = []
    for effect in state.template.regeneration:
        suppressed = bool(damage_types.intersection(effect.suppressed_by_damage_types))
        eligible = state.is_alive and not state.is_dead and (state.current_hp > 0 or not effect.requires_positive_hp)
        healed = _restore(state, effect.healing) if eligible and not suppressed else 0
        results.append(RegenerationResult(effect.id, healed, suppressed))
    state.damage_types_since_last_turn.clear()
    if started_at_zero and state.current_hp == 0:
        _die_at_zero(state)
    return results
