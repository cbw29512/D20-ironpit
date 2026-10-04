from __future__ import annotations

import logging

from app.combat.resources import resource_available, spend_resource
from app.combat.spell_caster_buffs import source_effect_is_active
from app.domain.runtime import CombatantState
from app.domain.spell_cast_modifiers import ResourceBackedSpellSaveDisadvantage

logger = logging.getLogger(__name__)


def _waived(
    state: CombatantState,
    option: ResourceBackedSpellSaveDisadvantage,
    turn_key: str | None,
) -> bool:
    if not source_effect_is_active(state, option.waived_while_source_effect_id):
        return False
    if option.waived_once_per_turn and turn_key is not None:
        return state.feature_last_turn_keys.get(option.id) != turn_key
    return True


def choose_spell_save_disadvantage(
    state: CombatantState,
    turn_key: str | None = None,
) -> ResourceBackedSpellSaveDisadvantage | None:
    """Choose the highest-priority legal resource-backed save Disadvantage option."""
    try:
        legal = [
            option
            for option in state.template.spell_save_disadvantage_options
            if resource_available(state, option.resource_id, option.resource_cost)
            or _waived(state, option, turn_key)
        ]
        return max(legal, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception(
            "Failed to choose spell-save Disadvantage option for %s.",
            state.template.name,
        )
        raise RuntimeError("Spell-save Disadvantage option could not be selected.") from exc


def spend_spell_save_disadvantage(
    state: CombatantState,
    option: ResourceBackedSpellSaveDisadvantage,
    turn_key: str | None = None,
) -> int | None:
    """Spend a declared resource only when the selected target is about to make its save."""
    try:
        if _waived(state, option, turn_key):
            if option.waived_once_per_turn and turn_key is not None:
                state.feature_last_turn_keys[option.id] = turn_key
            return None
        return spend_resource(state, option.resource_id, option.resource_cost)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to spend spell-save Disadvantage resource for %s.",
            state.template.name,
        )
        raise RuntimeError("Spell-save Disadvantage resource could not be spent.") from exc
