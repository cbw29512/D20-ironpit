from __future__ import annotations

from app.combat.grapple import (
    RESTRAINED_EFFECT_ID,
    apply_grapple,
    grapple_attack_disadvantage,
    speed_is_zero,
)
from app.domain.models import CombatantState, WeaponAttack
from app.domain.size import size_at_most

DODGE_EFFECT_ID = "dodge"
PRONE_EFFECT_ID = "prone"


def attack_roll_condition_sources(
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
    target_id: str | None = None,
) -> tuple[int, int]:
    """Return Advantage and Disadvantage sources from supported conditions."""
    advantage = 0
    disadvantage = 0
    if PRONE_EFFECT_ID in attacker.active_effect_ids:
        disadvantage += 1
    if RESTRAINED_EFFECT_ID in attacker.active_effect_ids:
        disadvantage += 1
    if target_id is not None:
        disadvantage += grapple_attack_disadvantage(attacker, target_id)
    if (
        DODGE_EFFECT_ID in defender.active_effect_ids
        and not defender.is_unconscious
        and not speed_is_zero(defender)
        and defender.template.speed_ft > 0
    ):
        disadvantage += 1
    if defender.is_unconscious:
        advantage += 1
    if RESTRAINED_EFFECT_ID in defender.active_effect_ids:
        advantage += 1
    if PRONE_EFFECT_ID in defender.active_effect_ids:
        if distance_ft <= 5:
            advantage += 1
        else:
            disadvantage += 1
    return advantage, disadvantage


def apply_hit_conditions(
    attack: WeaponAttack,
    defender: CombatantState,
    source_id: str,
) -> list[str]:
    """Apply certified automatic conditions from a successful weapon hit."""
    if defender.current_hp <= 0 or not defender.is_alive:
        return []
    applied: list[str] = []
    maximum = attack.knocks_prone_max_size
    if maximum is not None and size_at_most(defender.template.size, maximum):
        if PRONE_EFFECT_ID not in defender.active_effect_ids:
            defender.active_effect_ids.append(PRONE_EFFECT_ID)
        applied.append(PRONE_EFFECT_ID)
    control = attack.control_effect
    if control is not None and control.grapple_escape_dc is not None:
        if control.max_target_size is None or size_at_most(defender.template.size, control.max_target_size):
            applied.extend(apply_grapple(
                defender,
                source_id,
                control.grapple_escape_dc,
                attack.weapon.reach_ft,
                restrains=control.restrains_while_grappled,
            ))
    return list(dict.fromkeys(applied))


def stand_from_prone(state: CombatantState) -> int:
    """Spend half Speed at turn start to end Prone when standing is possible."""
    if PRONE_EFFECT_ID not in state.active_effect_ids or state.template.speed_ft <= 0 or speed_is_zero(state):
        return 0
    movement_cost = state.template.speed_ft // 2
    state.movement_remaining_ft = max(0, state.movement_remaining_ft - movement_cost)
    state.active_effect_ids.remove(PRONE_EFFECT_ID)
    return movement_cost
