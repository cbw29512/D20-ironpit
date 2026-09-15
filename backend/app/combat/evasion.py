from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.domain.actions import SavingThrowAction
from app.domain.runtime import CombatantState
from app.domain.traits import CombatTrait


def evasion_applies(state: CombatantState, action: SavingThrowAction) -> bool:
    """Return whether this save qualifies for the combatant's Evasion rules."""
    if CombatTrait.EVASION not in state.template.combat_traits:
        return False
    if action.save_ability != "dexterity" or action.success_damage != "half":
        return False
    return state.template.ruleset != "2024" or not is_incapacitated(state)


def save_damage_total(
    state: CombatantState,
    action: SavingThrowAction,
    succeeded: bool,
    raw_total: int,
) -> int:
    """Apply save-result damage, including Evasion, before damage defenses."""
    if evasion_applies(state, action):
        return 0 if succeeded else raw_total // 2
    if succeeded and action.success_damage == "half":
        return raw_total // 2
    return raw_total
