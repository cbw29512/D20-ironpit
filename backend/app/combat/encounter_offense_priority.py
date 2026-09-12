from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.charge import resolve_charge_closing
from app.combat.encounter_area_actions import resolve_ready_area_action
from app.combat.encounter_turn_support import recharge_action_ready, resolve_ready_recharge_action
from app.combat.pit_policy import target_order
from app.combat.spell_offense import resolve_best_spell_offense

logger = logging.getLogger(__name__)


def resolve_recharge_priority(sequence, round_number, attacker, setup, dice):
    try:
        area_events, sequence, fired = resolve_ready_area_action(
            sequence, round_number, attacker, setup, dice, recharge_only=True,
        )
        if fired:
            return area_events, sequence, True
        return resolve_ready_recharge_action(sequence, round_number, attacker, setup, dice)
    except Exception:
        logger.exception("Failed Recharge priority for %s.", attacker.combatant_id)
        raise


def resolve_pre_movement_offense(sequence, round_number, attacker, setup, turn_key, dice):
    """Resolve mandatory Recharge, ordinary spell offense, and Charge before movement."""
    try:
        events, sequence, fired = resolve_recharge_priority(
            sequence, round_number, attacker, setup, dice,
        )
        if fired:
            return events, sequence, True
        if not recharge_action_ready(attacker):
            spell_events, sequence = resolve_best_spell_offense(
                sequence, round_number, attacker, setup, turn_key, dice,
            )
            events.extend(spell_events)
            if not is_available(attacker.state, "action"):
                return events, sequence, True
        targets = target_order(attacker, setup)
        if not targets:
            return events, sequence, True
        charge_events, sequence, charged = resolve_charge_closing(
            sequence, round_number, attacker, targets[0], dice, setup,
        )
        events.extend(charge_events)
        handled = charged or attacker.state.is_dead or attacker.state.is_unconscious
        return events, sequence, handled
    except Exception:
        logger.exception("Failed pre-movement offense for %s.", attacker.combatant_id)
        raise


def resolve_post_movement_offense(sequence, round_number, attacker, setup, turn_key, dice):
    """Retry mandatory Recharge after movement, then allow ordinary spell offense."""
    try:
        events, sequence, fired = resolve_recharge_priority(
            sequence, round_number, attacker, setup, dice,
        )
        if fired:
            return events, sequence, True
        spell_events, sequence = resolve_best_spell_offense(
            sequence, round_number, attacker, setup, turn_key, dice,
        )
        events.extend(spell_events)
        return events, sequence, not is_available(attacker.state, "action")
    except Exception:
        logger.exception("Failed post-movement offense for %s.", attacker.combatant_id)
        raise
