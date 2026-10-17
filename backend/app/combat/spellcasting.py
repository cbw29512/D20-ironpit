from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def slot_spell_available(state: CombatantState, turn_key: str) -> bool:
    """Apply the one-slot-per-turn gate only to 2024 combatants."""
    try:
        if not turn_key:
            raise ValueError("Spell-slot legality requires an active turn key.")
        ruleset = state.template.ruleset
        if ruleset not in {"2014", "2024"}:
            raise ValueError(f"Unsupported spellcasting ruleset: {ruleset!r}.")
        return ruleset == "2014" or state.spell_slot_expended_turn_key != turn_key
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



def spell_turn_legal(state: CombatantState, turn_key: str, action_cost: str, spell_level: int) -> bool:
    """Source-neutral spell timing gate; callers must still check slots and actions."""
    try:
        if not turn_key or action_cost not in {"action", "bonus_action", "reaction"}:
            raise ValueError("A spell requires a turn key and supported casting action.")
        if not 0 <= spell_level <= 9:
            raise ValueError("Spell level must be between 0 and 9.")
        if state.template.ruleset == "2024":
            return spell_level == 0 or slot_spell_available(state, turn_key)
        if state.template.ruleset != "2014":
            raise ValueError("Unsupported spellcasting ruleset.")
        history = state.feature_last_turn_keys
        if action_cost == "bonus_action":
            return history.get("spell:action-noncantrip") != turn_key
        if history.get("spell:bonus-action") == turn_key:
            return action_cost == "action" and spell_level == 0
        return True
    except ValueError:
        raise
    except Exception:
        logger.exception("Failed spell turn legality for %s.", state.template.id)
        raise


def record_spell_turn(state: CombatantState, turn_key: str, action_cost: str, spell_level: int) -> None:
    """Record a successful cast in temporary fight state, without spending a resource."""
    try:
        if not spell_turn_legal(state, turn_key, action_cost, spell_level):
            raise ValueError("Spell conflicts with another cast on this turn.")
        if state.template.ruleset == "2014":
            if action_cost == "bonus_action":
                state.feature_last_turn_keys["spell:bonus-action"] = turn_key
            elif spell_level > 0 or action_cost == "reaction":
                state.feature_last_turn_keys["spell:action-noncantrip"] = turn_key
    except ValueError:
        raise
    except Exception:
        logger.exception("Failed to record spell turn for %s.", state.template.id)
        raise

def legal_slot_levels(
    state: CombatantState,
    turn_key: str,
    printed_level: int,
    *,
    higher_slot_scaling: bool = False,
) -> tuple[int, ...]:
    """Return spell-slot levels Iron Pit may legally choose for one declared spell."""
    try:
        if printed_level == 0:
            return (0,)
        if not 1 <= printed_level <= 9:
            raise ValueError("Printed spell level must be between 0 and 9.")
        if not slot_spell_available(state, turn_key):
            return ()
        maximum = 9 if higher_slot_scaling else printed_level
        available: list[int] = []
        for level in range(printed_level, maximum + 1):
            resource_id = f"spell-slot-{level}"
            resource = next((item for item in state.resources if item.id == resource_id), None)
            if resource is not None and resource.current_uses > 0:
                available.append(level)
        return tuple(available)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to determine legal spell slots for %s.", state.template.id)
        raise RuntimeError("Legal spell-slot levels could not be evaluated.") from exc
