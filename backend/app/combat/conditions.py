from __future__ import annotations

import logging

from app.domain.models import AbilityKind, CombatantState, ConditionKind

logger = logging.getLogger(__name__)

INCAPACITATING_CONDITIONS = {
    ConditionKind.INCAPACITATED,
    ConditionKind.PARALYZED,
}


def has_condition(state: CombatantState, condition: ConditionKind) -> bool:
    try:
        if condition is ConditionKind.INCAPACITATED:
            return bool(state.conditions & INCAPACITATING_CONDITIONS)
        return condition in state.conditions
    except Exception as exc:
        logger.exception("Failed to read condition state for %s.", state.template.name)
        raise RuntimeError("Condition state could not be resolved.") from exc


def is_incapacitated(state: CombatantState) -> bool:
    return has_condition(state, ConditionKind.INCAPACITATED)


def effective_speed_ft(state: CombatantState) -> int:
    try:
        return 0 if has_condition(state, ConditionKind.PARALYZED) else state.template.speed_ft
    except Exception as exc:
        logger.exception("Failed to resolve effective Speed for %s.", state.template.name)
        raise RuntimeError("Effective Speed could not be resolved.") from exc


def require_activity(state: CombatantState, activity: str) -> None:
    """Reject an Action, Bonus Action, or Reaction while Incapacitated."""
    try:
        if is_incapacitated(state):
            raise ValueError(f"Incapacitated creatures cannot take a {activity}.")
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to validate %s permission for %s.", activity, state.template.name)
        raise RuntimeError("Activity permission could not be resolved.") from exc


def automatically_fails_save(state: CombatantState, ability: AbilityKind) -> bool:
    try:
        return (
            has_condition(state, ConditionKind.PARALYZED)
            and ability in {AbilityKind.STRENGTH, AbilityKind.DEXTERITY}
        )
    except Exception as exc:
        logger.exception("Failed to resolve automatic save failure for %s.", state.template.name)
        raise RuntimeError("Automatic save failure could not be resolved.") from exc


def resolve_condition_attack_sources(defender: CombatantState) -> tuple[int, int]:
    try:
        advantage = int(has_condition(defender, ConditionKind.PARALYZED))
        return advantage, 0
    except Exception as exc:
        logger.exception("Failed to resolve condition attack effects for %s.", defender.template.name)
        raise RuntimeError("Condition attack effects could not be resolved.") from exc


def is_automatic_critical_hit(defender: CombatantState, distance_ft: int) -> bool:
    try:
        return has_condition(defender, ConditionKind.PARALYZED) and distance_ft <= 5
    except Exception as exc:
        logger.exception("Failed to resolve automatic critical hit for %s.", defender.template.name)
        raise RuntimeError("Automatic critical hit could not be resolved.") from exc
