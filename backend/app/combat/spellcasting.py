from __future__ import annotations

import logging

from app.domain.models import CombatantState
from app.domain.spell_cast_grants import FreeSpellCastGrant

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



def available_free_spell_cast(
    state: CombatantState,
    spell_id: str,
) -> FreeSpellCastGrant | None:
    """Return the first usable source-owned free-cast grant for one spell."""
    try:
        for grant in state.template.progression_features.free_spell_cast_grants:
            if grant.spell_id != spell_id:
                continue
            if grant.resource_id is None:
                return grant
            resource = next(
                (item for item in state.resources if item.id == grant.resource_id),
                None,
            )
            if resource is None:
                raise ValueError(
                    f"Free spell cast {grant.source_id} references missing resource {grant.resource_id}."
                )
            if resource.current_uses >= grant.resource_cost:
                return grant
        return None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to resolve free spell-cast availability for %s spell=%s.",
            state.template.id,
            spell_id,
        )
        raise RuntimeError("Free spell-cast availability could not be resolved.") from exc


def consume_free_spell_cast(
    state: CombatantState,
    grant: FreeSpellCastGrant,
) -> int | None:
    """Consume only the grant's own finite resource; at-will grants mutate nothing."""
    try:
        if grant.resource_id is None:
            return None
        resource = next(
            (item for item in state.resources if item.id == grant.resource_id),
            None,
        )
        if resource is None:
            raise ValueError(
                f"Free spell cast {grant.source_id} references missing resource {grant.resource_id}."
            )
        if resource.current_uses < grant.resource_cost:
            raise ValueError(f"{grant.source_name} has no uses remaining.")
        resource.current_uses -= grant.resource_cost
        return resource.current_uses
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to consume free spell-cast grant %s for %s.",
            grant.source_id,
            state.template.id,
        )
        raise RuntimeError("Free spell-cast grant could not be consumed.") from exc
