from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def slot_spell_available(state: CombatantState, turn_key: str) -> bool:
    """2024: a creature can expend only one spell slot to cast a spell on a turn."""
    try:
        if not turn_key:
            raise ValueError("Spell-slot legality requires an active turn key.")
        return state.spell_slot_expended_turn_key != turn_key
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to evaluate spell-slot turn gate for %s.", state.template.id)
        raise RuntimeError("Spell-slot turn legality could not be evaluated.") from exc


def mark_slot_spell_cast(state: CombatantState, turn_key: str) -> None:
    """Record the turn on which this creature expended a spell slot to cast a spell."""
    try:
        if not slot_spell_available(state, turn_key):
            raise ValueError("A spell slot has already been expended to cast a spell on this turn.")
        state.spell_slot_expended_turn_key = turn_key
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to mark spell-slot expenditure for %s.", state.template.id)
        raise RuntimeError("Spell-slot expenditure could not be recorded.") from exc
