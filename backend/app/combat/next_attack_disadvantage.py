from __future__ import annotations

import logging

from app.combat.timed_condition_lifecycle import remove_effect_group
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def next_attack_disadvantage_sources(state: CombatantState) -> int:
    """Count active timed effects that impose Disadvantage on the next attack roll."""
    try:
        return sum(1 for effect in state.timed_effects if effect.next_attack_disadvantage)
    except Exception as exc:
        logger.exception("Next-attack Disadvantage lookup failed for %s.", state.template.name)
        raise RuntimeError("Next-attack Disadvantage could not be evaluated.") from exc


def consume_next_attack_disadvantage(state: CombatantState) -> int:
    """Consume all active next-attack Disadvantage groups after one attack roll."""
    try:
        consumed = 0
        for effect in list(state.timed_effects):
            if not effect.next_attack_disadvantage or effect not in state.timed_effects:
                continue
            if remove_effect_group(state, effect):
                consumed += 1
        return consumed
    except Exception as exc:
        logger.exception("Next-attack Disadvantage consumption failed for %s.", state.template.name)
        raise RuntimeError("Next-attack Disadvantage could not be consumed.") from exc
