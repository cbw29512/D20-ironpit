from __future__ import annotations

from app.domain.models import CombatantState


def d20_modifier(state: CombatantState) -> int:
    """Return the 2024 Exhaustion penalty for a D20 Test; 2014 uses Disadvantage instead."""
    if state.template.ruleset == "2024":
        return -2 * state.exhaustion_level
    return 0


def ability_check_disadvantage_sources(state: CombatantState) -> int:
    """2014 Exhaustion level 1+: Disadvantage on ability checks."""
    return int(state.template.ruleset == "2014" and state.exhaustion_level >= 1)


def attack_disadvantage_sources(state: CombatantState) -> int:
    """2014 Exhaustion level 3+: Disadvantage on attack rolls."""
    return int(state.template.ruleset == "2014" and state.exhaustion_level >= 3)


def saving_throw_disadvantage_sources(state: CombatantState) -> int:
    """2014 Exhaustion level 3+: Disadvantage on saving throws."""
    return int(state.template.ruleset == "2014" and state.exhaustion_level >= 3)


def speed_after_exhaustion(state: CombatantState, speed: int) -> int:
    if state.template.ruleset == "2014":
        if state.exhaustion_level >= 5:
            return 0
        if state.exhaustion_level >= 2:
            return speed // 2
        return speed
    return max(0, speed - (5 * state.exhaustion_level))


def max_hp_after_exhaustion(state: CombatantState, maximum: int) -> int:
    if state.template.ruleset == "2014" and state.exhaustion_level >= 4:
        return maximum // 2
    return maximum


def gain_exhaustion(state: CombatantState, levels: int = 1) -> int:
    """Gain cumulative Exhaustion using the active ruleset's six-level track."""
    if levels < 0:
        raise ValueError("Exhaustion gain cannot be negative.")
    state.exhaustion_level = min(6, state.exhaustion_level + levels)
    maximum = max_hp_after_exhaustion(state, state.template.max_hp + state.max_hp_bonus)
    state.current_hp = min(state.current_hp, maximum)
    if state.exhaustion_level >= 6:
        state.current_hp = 0
        state.is_alive = False
        state.is_unconscious = False
        state.is_stable = False
        state.is_dead = True
    return state.exhaustion_level


def reduce_exhaustion(state: CombatantState, levels: int = 1) -> int:
    if levels < 0:
        raise ValueError("Exhaustion reduction cannot be negative.")
    state.exhaustion_level = max(0, state.exhaustion_level - levels)
    return state.exhaustion_level
