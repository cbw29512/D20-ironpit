from __future__ import annotations

import logging

from app.combat.resources import action_resource_available, resolved_resource_id
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


def spell_action_resource_available(
    state: CombatantState,
    *,
    level: int,
    resource_id: str | None,
    resource_cost: int,
    turn_key: str,
) -> bool:
    """Mirror resolver resource legality for attack, save, and automatic spells."""
    try:
        if level < 0:
            raise ValueError("Spell level cannot be negative.")
        fallback_id = f"spell-slot-{level}" if level > 0 else None
        resolved = resolved_resource_id(resource_id, fallback_id)
        uses_spell_slot = bool(resolved and resolved.startswith("spell-slot-"))
        if uses_spell_slot and not slot_spell_available(state, turn_key):
            return False
        return action_resource_available(
            state,
            resource_id,
            resource_cost,
            fallback_resource_id=fallback_id,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed spell resource legality check for %s.", state.template.id)
        raise RuntimeError("Spell resource legality could not be evaluated.") from exc


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
