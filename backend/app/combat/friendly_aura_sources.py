from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition, is_incapacitated
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)
_PREFIX = "friendly-save-aura:"
_COVER_PREFIX = "friendly-cover-aura:"
_CONDITION_PREFIX = "friendly-condition-aura:"

def _active(source: EncounterCombatant, action_id: str, passive: bool = False) -> bool:
    try:
        state = source.state
        if state.is_dead or not state.is_alive or state.current_hp <= 0:
            return False
        if passive:
            return True
        if is_incapacitated(state):
            return False
        return any(
            effect.source_id == source.combatant_id and effect.source_effect_id == action_id
            for effect in state.timed_effects
        )
    except Exception:
        logger.exception("Failed to evaluate friendly save-aura source %s.", source.combatant_id)
        raise


def _passive_active(source: EncounterCombatant, aura) -> bool:
    try:
        state = source.state
        if state.is_dead or not state.is_alive or state.current_hp <= 0:
            return False
        if aura.inactive_while_incapacitated and is_incapacitated(state):
            return False
        if aura.inactive_while_unconscious and (
            state.is_unconscious or has_condition(state, "unconscious")
        ):
            return False
        return True
    except Exception:
        logger.exception("Failed to evaluate passive friendly save-aura source %s.", source.combatant_id)
        raise


def _clear(setup: EncounterSetup) -> None:
    try:
        for member in [*setup.heroes, *setup.monsters]:
            member.state.active_modifiers = [
                item for item in member.state.active_modifiers
                if not item.id.startswith(_PREFIX) and not item.id.startswith(_COVER_PREFIX)
                and not item.id.startswith(_CONDITION_PREFIX)
            ]
    except Exception:
        logger.exception("Failed clearing source-owned friendly aura modifiers.")
        raise
