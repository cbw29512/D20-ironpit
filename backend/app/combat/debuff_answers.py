from __future__ import annotations

import logging

from typing import get_args

from app.combat.condition_rules import has_condition
from app.domain.action_types import ConditionName
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)

COUNTER_KINDS = frozenset({"condition-immunity", "debuff-counter"})
CONDITION_IDS = frozenset(get_args(ConditionName))


def active_condition_ids(state) -> list[str]:
    try:
        seen: list[str] = []
        for effect_id in state.active_effect_ids:
            if effect_id in CONDITION_IDS and effect_id not in seen and has_condition(state, effect_id):
                seen.append(effect_id)
        return seen
    except Exception:
        logger.exception("Failed active-condition scan for %s.", getattr(state.template, "name", "unknown"))
        raise


def suppressed_condition_ids(state) -> list[str]:
    try:
        seen: list[str] = []
        for effect_id in state.active_effect_ids:
            if effect_id in CONDITION_IDS and effect_id not in seen and not has_condition(state, effect_id):
                seen.append(effect_id)
        return seen
    except Exception:
        logger.exception("Failed suppressed-condition scan for %s.", getattr(state.template, "name", "unknown"))
        raise


def countered_condition_ids(action: SpellSaveAction) -> set[str]:
    try:
        answered: set[str] = set()
        for effect in action.failed_save_modifier_effects:
            if effect.kind == "condition-immunity" and effect.condition_id:
                answered.add(str(effect.condition_id))
            counter = effect.debuff_counter
            if effect.kind == "debuff-counter" and counter is not None and counter.debuff_id:
                answered.add(str(counter.debuff_id))
        return answered
    except Exception:
        logger.exception("Failed to read countered conditions for %s.", action.id)
        raise


def failed_save_is_beneficial(action: SpellSaveAction) -> bool:
    try:
        if action.damage_dice_count or action.damage_components or action.failed_save_timed_effect:
            return False
        kinds = {str(effect.kind) for effect in action.failed_save_modifier_effects}
        return bool(kinds) and kinds <= COUNTER_KINDS
    except Exception:
        logger.exception("Failed beneficial-save check for %s.", action.id)
        raise
