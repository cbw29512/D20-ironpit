from __future__ import annotations

import logging
from typing import Literal

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)
SpellActionCost = Literal["action", "bonus_action", "reaction"]


def _validate_turn_key(turn_key: str) -> None:
    if not turn_key:
        raise ValueError("Spell-cast legality requires an active turn key.")


def _is_action_cantrip(spell_level: int, action_cost: SpellActionCost) -> bool:
    return spell_level == 0 and action_cost == "action"


def spell_level_from_resource_id(resource_id: str | None) -> int | None:
    if not resource_id or not resource_id.startswith("spell-slot-"):
        return None
    try:
        level = int(resource_id.removeprefix("spell-slot-"))
    except ValueError as exc:
        raise ValueError(f"Invalid spell-slot resource id {resource_id!r}.") from exc
    if not 1 <= level <= 9:
        raise ValueError(f"Spell-slot resource level must be 1-9, got {level}.")
    return level


def spell_cast_available(
    state: CombatantState,
    turn_key: str,
    spell_level: int,
    action_cost: SpellActionCost,
    *,
    expends_spell_slot: bool,
) -> bool:
    """Apply the edition-correct per-turn spellcasting restriction.

    2014: after any Bonus Action spell, the only other spell on that turn may be
    a cantrip with a casting time of 1 Action. A Bonus Action spell is itself
    illegal if a non-Action-cantrip spell has already been cast that turn.

    2024: a creature can expend only one spell slot to cast a spell on a turn.
    """
    try:
        _validate_turn_key(turn_key)
        if not 0 <= spell_level <= 9:
            raise ValueError("Spell level must be between 0 and 9.")
        ruleset = state.template.ruleset
        if ruleset == "2024":
            return not (
                expends_spell_slot
                and state.spell_slot_expended_turn_key == turn_key
            )
        if ruleset == "2014":
            if action_cost == "bonus_action":
                return state.non_action_cantrip_spell_cast_turn_key != turn_key
            if _is_action_cantrip(spell_level, action_cost):
                return True
            return state.bonus_action_spell_cast_turn_key != turn_key
        raise ValueError(f"Unsupported spellcasting ruleset {ruleset!r}.")
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to evaluate spell-cast turn legality for %s.", state.template.id)
        raise RuntimeError("Spell-cast turn legality could not be evaluated.") from exc


def mark_spell_cast(
    state: CombatantState,
    turn_key: str,
    spell_level: int,
    action_cost: SpellActionCost,
    *,
    expends_spell_slot: bool,
) -> None:
    """Record only the per-turn facts required by the active edition."""
    try:
        if not spell_cast_available(
            state,
            turn_key,
            spell_level,
            action_cost,
            expends_spell_slot=expends_spell_slot,
        ):
            raise ValueError("Spell cannot be cast under the active edition's per-turn casting rule.")
        if state.template.ruleset == "2024":
            if expends_spell_slot:
                state.spell_slot_expended_turn_key = turn_key
            return
        if action_cost == "bonus_action":
            state.bonus_action_spell_cast_turn_key = turn_key
            state.non_action_cantrip_spell_cast_turn_key = turn_key
        elif not _is_action_cantrip(spell_level, action_cost):
            state.non_action_cantrip_spell_cast_turn_key = turn_key
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to mark spell cast for %s.", state.template.id)
        raise RuntimeError("Spell cast could not be recorded.") from exc


def slot_spell_available(
    state: CombatantState,
    turn_key: str,
    *,
    spell_level: int = 1,
    action_cost: SpellActionCost = "action",
) -> bool:
    """Compatibility wrapper for a spell that expends a slot."""
    return spell_cast_available(
        state,
        turn_key,
        spell_level,
        action_cost,
        expends_spell_slot=True,
    )


def mark_slot_spell_cast(
    state: CombatantState,
    turn_key: str,
    *,
    spell_level: int = 1,
    action_cost: SpellActionCost = "action",
) -> None:
    """Compatibility wrapper for recording a spell that expends a slot."""
    mark_spell_cast(
        state,
        turn_key,
        spell_level,
        action_cost,
        expends_spell_slot=True,
    )


def legal_slot_levels(
    state: CombatantState,
    turn_key: str,
    printed_level: int,
    *,
    action_cost: SpellActionCost = "action",
    higher_slot_scaling: bool = False,
) -> tuple[int, ...]:
    """Return slot levels allowed by resources and edition-correct casting rules."""
    try:
        if not 0 <= printed_level <= 9:
            raise ValueError("Printed spell level must be between 0 and 9.")
        if printed_level == 0:
            return (0,) if spell_cast_available(
                state,
                turn_key,
                0,
                action_cost,
                expends_spell_slot=False,
            ) else ()
        if not slot_spell_available(
            state,
            turn_key,
            spell_level=printed_level,
            action_cost=action_cost,
        ):
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
