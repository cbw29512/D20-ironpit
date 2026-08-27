from __future__ import annotations

from app.combat.conditions import condition_states, has_condition
from app.domain.models import Ability, CombatantState, ConditionType


def _visible_fear(state: CombatantState, visible_source_ids: set[str] | None) -> bool:
    if not visible_source_ids:
        return False
    return any(
        item.source_id in visible_source_ids
        for item in condition_states(state, ConditionType.FRIGHTENED)
        if item.source_id is not None
    )


def is_incapacitated(state: CombatantState) -> bool:
    return any(
        has_condition(state, condition)
        for condition in (ConditionType.INCAPACITATED, ConditionType.PARALYZED)
    )


def has_zero_speed(state: CombatantState) -> bool:
    return any(
        has_condition(state, condition)
        for condition in (ConditionType.GRAPPLED, ConditionType.PARALYZED, ConditionType.RESTRAINED)
    )


def ability_check_condition_sources(
    state: CombatantState,
    visible_source_ids: set[str] | None = None,
) -> tuple[int, int]:
    disadvantage = int(has_condition(state, ConditionType.POISONED))
    disadvantage += int(_visible_fear(state, visible_source_ids))
    return 0, disadvantage


def saving_throw_condition_sources(
    state: CombatantState,
    ability: Ability,
) -> tuple[int, int, bool]:
    auto_fail = has_condition(state, ConditionType.PARALYZED) and ability in {
        Ability.STRENGTH,
        Ability.DEXTERITY,
    }
    disadvantage = int(
        has_condition(state, ConditionType.RESTRAINED) and ability is Ability.DEXTERITY
    )
    return 0, disadvantage, auto_fail


def attack_condition_sources(
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
    visible_source_ids: set[str] | None = None,
) -> tuple[int, int]:
    advantage = int(has_condition(defender, ConditionType.PARALYZED))
    disadvantage = int(has_condition(attacker, ConditionType.PRONE))
    disadvantage += int(has_condition(attacker, ConditionType.POISONED))
    disadvantage += int(_visible_fear(attacker, visible_source_ids))

    grapples = condition_states(attacker, ConditionType.GRAPPLED)
    if any(item.source_id != defender.instance_id for item in grapples):
        disadvantage += 1
    if has_condition(defender, ConditionType.PRONE):
        if distance_ft <= 5:
            advantage += 1
        else:
            disadvantage += 1
    if has_condition(defender, ConditionType.RESTRAINED):
        advantage += 1
    if has_condition(attacker, ConditionType.RESTRAINED):
        disadvantage += 1
    return advantage, disadvantage


def is_auto_critical_hit(defender: CombatantState, distance_ft: int) -> bool:
    return distance_ft <= 5 and has_condition(defender, ConditionType.PARALYZED)
