from __future__ import annotations

from app.domain.models import CombatantState, WeaponAttack
from app.domain.size import size_at_most

DODGE_EFFECT_ID = "dodge"
PRONE_EFFECT_ID = "prone"


def attack_roll_condition_sources(
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
) -> tuple[int, int]:
    """Return Advantage and Disadvantage sources from supported conditions."""
    advantage = 0
    disadvantage = 0
    if PRONE_EFFECT_ID in attacker.active_effect_ids:
        disadvantage += 1
    if (
        DODGE_EFFECT_ID in defender.active_effect_ids
        and not defender.is_unconscious
        and defender.template.speed_ft > 0
    ):
        disadvantage += 1
    if defender.is_unconscious:
        advantage += 1
    if PRONE_EFFECT_ID in defender.active_effect_ids:
        if distance_ft <= 5:
            advantage += 1
        else:
            disadvantage += 1
    return advantage, disadvantage


def apply_hit_conditions(attack: WeaponAttack, defender: CombatantState) -> list[str]:
    """Apply certified automatic conditions from a successful weapon hit."""
    maximum = attack.knocks_prone_max_size
    if (
        maximum is not None
        and defender.current_hp > 0
        and defender.is_alive
        and size_at_most(defender.template.size, maximum)
    ):
        if PRONE_EFFECT_ID not in defender.active_effect_ids:
            defender.active_effect_ids.append(PRONE_EFFECT_ID)
        return [PRONE_EFFECT_ID]
    return []


def stand_from_prone(state: CombatantState) -> int:
    """Spend half Speed at turn start to end Prone when standing is possible."""
    if PRONE_EFFECT_ID not in state.active_effect_ids or state.template.speed_ft <= 0:
        return 0
    movement_cost = state.template.speed_ft // 2
    state.movement_remaining_ft = max(0, state.movement_remaining_ft - movement_cost)
    state.active_effect_ids.remove(PRONE_EFFECT_ID)
    return movement_cost
