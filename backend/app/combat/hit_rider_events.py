"""Bind declarative hit riders to every completed attack-event path."""
from __future__ import annotations

import logging
from app.combat.damage_event_context import _member_by_id
from app.combat.modifier_stack import effective_speed
from app.combat.policy import weapon_attack_profiles
from app.combat.post_hit_save_condition import resolve_post_hit_save_condition
from app.combat.resource_backed_on_hit_save import resolve_resource_backed_on_hit_save

logger = logging.getLogger(__name__)


def resolve_hit_rider_event(sequence, round_number, source, event, setup, dice, turn_key):
    try:
        if not event.hit:
            return [], sequence
        target = _member_by_id(setup, event.target_id)
        if target is None:
            raise ValueError("Hit rider target is absent from the encounter.")
        events = []
        if turn_key:
            save_event = resolve_post_hit_save_condition(
                sequence, round_number, source, target, setup, dice, turn_key,
            )
            if save_event is not None:
                events.append(save_event)
                sequence += 1
        rider = source.state.template.progression_features.resource_backed_on_hit_save_rider
        if rider is None:
            return events, sequence
        if not turn_key:
            raise ValueError("Hit rider requires the authoritative active turn key.")
        if not event.attack_id:
            raise ValueError("Hit rider requires the resolved attack identity.")
        if event.attack_id not in rider.trigger_attack_ids:
            return events, sequence
        attack = next((item for item in weapon_attack_profiles(source.state)
                       if item.id == event.attack_id), None)
        if attack is None:
            raise ValueError("Hit rider attack is absent from the certified profiles.")
        speed_before = effective_speed(target.state)
        result = resolve_resource_backed_on_hit_save(
            sequence, round_number, source, target, attack, dice, turn_key,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
            setup=setup,
        )
        if turn_key == f"{round_number}:{target.combatant_id}":
            delta = effective_speed(target.state) - speed_before
            target.state.movement_remaining_ft = max(
                0, target.state.movement_remaining_ft + delta * (1 + target.state.dash_uses_this_turn),
            )
        if result:
            events.append(result.event)
            sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Hit rider event dispatch failed: actor=%s event=%s.",
                         source.combatant_id, event.sequence)
        raise
