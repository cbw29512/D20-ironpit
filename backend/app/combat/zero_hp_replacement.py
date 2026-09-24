from __future__ import annotations

import logging

from app.combat.modifier_stack import remove_source_modifiers
from app.domain.modifiers import ModifierKind
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def _replacement(state: CombatantState):
    choices = [
        item for item in state.active_modifiers
        if item.kind is ModifierKind.ZERO_HP_REPLACEMENT
    ]
    return max(choices, key=lambda item: (item.replacement_hp, item.id), default=None)


def _consume(state: CombatantState, modifier, reason: str) -> None:
    remove_source_modifiers([state], modifier.source_id, modifier.source_effect_id)
    state.active_buff_effect_ids = [
        item for item in state.active_buff_effect_ids
        if item != modifier.source_effect_id
    ]
    source_name = modifier.source_name or modifier.source_effect_id
    state.pending_zero_hp_replacement_logs.append(
        f"{source_name} {reason}"
    )


def consume_zero_hp_replacement(state: CombatantState) -> bool:
    """Consume the strongest active source-owned replacement for a drop to 0 HP."""
    try:
        modifier = _replacement(state)
        if modifier is None:
            return False
        state.current_hp = modifier.replacement_hp
        state.is_alive = True
        state.is_dead = False
        state.is_unconscious = False
        state.is_stable = False
        state.death_save_successes = 0
        state.death_save_failures = 0
        _consume(
            state,
            modifier,
            f"prevents the drop to 0 HP; {state.template.name} remains at {modifier.replacement_hp} HP.",
        )
        return True
    except Exception:
        logger.exception("Zero-HP replacement failed for %s.", state.template.id)
        raise


def consume_instant_death_prevention(state: CombatantState) -> bool:
    """Consume a source-owned ward that negates a non-damage instant-death effect."""
    try:
        choices = [
            item for item in state.active_modifiers
            if item.kind is ModifierKind.ZERO_HP_REPLACEMENT and item.prevents_instant_death
        ]
        modifier = max(choices, key=lambda item: (item.replacement_hp, item.id), default=None)
        if modifier is None:
            return False
        _consume(
            state,
            modifier,
            f"negates an instant-death effect against {state.template.name}.",
        )
        return True
    except Exception:
        logger.exception("Instant-death prevention failed for %s.", state.template.id)
        raise


def consume_zero_hp_replacement_log(state: CombatantState) -> str:
    try:
        result = " ".join(state.pending_zero_hp_replacement_logs)
        state.pending_zero_hp_replacement_logs.clear()
        return f" {result}" if result else ""
    except Exception:
        logger.exception("Zero-HP replacement audit failed for %s.", state.template.id)
        raise
