from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.aura_activation import resolve_ready_activated_aura
from app.combat.charge import resolve_charge_closing
from app.combat.death_triggers import append_pending_death_triggers
from app.combat.encounter_area_actions import resolve_ready_area_action
from app.combat.encounter_turn_support import recharge_action_ready, resolve_ready_recharge_action
from app.combat.pit_policy import target_order
from app.combat.self_buffs import activate_self_buff, choose_ready_self_buff
from app.combat.spell_offense import resolve_best_spell_offense
from app.combat.swallow import resolve_swallow_action

logger = logging.getLogger(__name__)


def _flush(events, sequence, round_number, setup, dice):
    return append_pending_death_triggers(events, sequence, round_number, setup, dice)


def resolve_recharge_priority(sequence, round_number, attacker, setup, dice):
    try:
        self_buff = choose_ready_self_buff(attacker.state)
        if self_buff is not None and is_available(attacker.state, "action"):
            return [activate_self_buff(sequence, round_number, attacker, self_buff)], sequence + 1, True
        area_events, sequence, fired = resolve_ready_area_action(
            sequence, round_number, attacker, setup, dice, recharge_only=True,
        )
        if fired:
            sequence = _flush(area_events, sequence, round_number, setup, dice)
            return area_events, sequence, True
        events, sequence, fired = resolve_ready_recharge_action(sequence, round_number, attacker, setup, dice)
        if fired:
            sequence = _flush(events, sequence, round_number, setup, dice)
        return events, sequence, fired
    except Exception:
        logger.exception("Failed Recharge priority for %s.", attacker.combatant_id)
        raise


def _resolve_aura_priority(sequence, round_number, attacker, setup, dice):
    try:
        events, sequence, fired = resolve_ready_activated_aura(
            sequence, round_number, attacker, setup,
        )
        if fired:
            sequence = _flush(events, sequence, round_number, setup, dice)
        return events, sequence, fired
    except Exception:
        logger.exception("Failed activated-aura priority for %s.", attacker.combatant_id)
        raise


def resolve_pre_movement_offense(sequence, round_number, attacker, setup, turn_key, dice):
    """Resolve priority offense that is already legal before ordinary movement."""
    try:
        events, sequence, fired = resolve_recharge_priority(sequence, round_number, attacker, setup, dice)
        if fired:
            return events, sequence, True
        aura_events, sequence, fired = _resolve_aura_priority(sequence, round_number, attacker, setup, dice)
        events.extend(aura_events)
        if fired:
            return events, sequence, True
        swallow_events, sequence, swallowed = resolve_swallow_action(sequence, round_number, attacker, setup, dice)
        events.extend(swallow_events)
        if swallow_events:
            sequence = _flush(events, sequence, round_number, setup, dice)
        if swallowed or attacker.state.is_dead:
            return events, sequence, True
        if not recharge_action_ready(attacker):
            spell_events, sequence = resolve_best_spell_offense(sequence, round_number, attacker, setup, turn_key, dice)
            events.extend(spell_events)
            if spell_events:
                sequence = _flush(events, sequence, round_number, setup, dice)
            if not is_available(attacker.state, "action") or attacker.state.is_dead:
                return events, sequence, True
        targets = target_order(attacker, setup)
        if not targets:
            return events, sequence, True
        charge_events, sequence, charged = resolve_charge_closing(sequence, round_number, attacker, targets[0], dice, setup)
        events.extend(charge_events)
        handled = charged or attacker.state.is_dead or attacker.state.is_unconscious
        return events, sequence, handled
    except Exception:
        logger.exception("Failed pre-movement offense for %s.", attacker.combatant_id)
        raise


def resolve_post_movement_offense(sequence, round_number, attacker, setup, turn_key, dice):
    """Retry priority offense after movement, then allow ordinary spell offense."""
    try:
        events, sequence, fired = resolve_recharge_priority(sequence, round_number, attacker, setup, dice)
        if fired:
            return events, sequence, True
        aura_events, sequence, fired = _resolve_aura_priority(sequence, round_number, attacker, setup, dice)
        events.extend(aura_events)
        if fired:
            return events, sequence, True
        swallow_events, sequence, swallowed = resolve_swallow_action(sequence, round_number, attacker, setup, dice)
        events.extend(swallow_events)
        if swallow_events:
            sequence = _flush(events, sequence, round_number, setup, dice)
        if swallowed or attacker.state.is_dead:
            return events, sequence, True
        spell_events, sequence = resolve_best_spell_offense(sequence, round_number, attacker, setup, turn_key, dice)
        events.extend(spell_events)
        if spell_events:
            sequence = _flush(events, sequence, round_number, setup, dice)
        return events, sequence, attacker.state.is_dead or not is_available(attacker.state, "action")
    except Exception:
        logger.exception("Failed post-movement offense for %s.", attacker.combatant_id)
        raise
