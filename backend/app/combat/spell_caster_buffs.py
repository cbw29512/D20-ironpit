from __future__ import annotations

import logging

from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def _active_spell_buffs(state: CombatantState):
    try:
        active_ids = {
            effect.source_effect_id
            for effect in state.timed_effects
            if effect.source_effect_id
        }
        for action in state.template.timed_self_buff_actions:
            if action.id in active_ids:
                yield action
    except Exception:
        logger.exception("Failed to scan active spell-caster buffs for %s.", state.template.name)
        raise


def active_spell_save_dc_bonus(state: CombatantState) -> int:
    try:
        return sum(action.spell_save_dc_bonus for action in _active_spell_buffs(state))
    except Exception:
        logger.exception("Failed to resolve spell save DC bonus for %s.", state.template.name)
        raise


def active_spell_attack_advantage(state: CombatantState) -> bool:
    try:
        return any(action.spell_attack_advantage for action in _active_spell_buffs(state))
    except Exception:
        logger.exception("Failed to resolve spell-attack Advantage for %s.", state.template.name)
        raise


def source_effect_is_active(state: CombatantState, effect_id: str | None) -> bool:
    try:
        if not effect_id:
            return False
        return any(effect.source_effect_id == effect_id for effect in state.timed_effects)
    except Exception:
        logger.exception("Failed to check timed source effect %s for %s.", effect_id, state.template.name)
        raise
