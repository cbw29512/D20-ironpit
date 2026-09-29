from __future__ import annotations

from app.combat.hp_threshold_condition import choose_hp_threshold_condition, resolve_hp_threshold_condition
from app.combat.hp_threshold_instant_death import (
    choose_hp_threshold_instant_death_targets,
    resolve_group_hp_threshold_instant_death,
)


def resolve_hp_threshold_turn(sequence, round_number, actor, setup, dice=None):
    """Resolve the highest-priority legal HP-threshold action, if any."""
    instant = choose_hp_threshold_instant_death_targets(actor, setup)
    if instant is not None:
        targets, action = instant
        events = resolve_group_hp_threshold_instant_death(
            sequence, round_number, actor, targets, action, setup, dice=dice,
        )
        return events, sequence + len(events)

    condition = choose_hp_threshold_condition(actor, setup)
    if condition is not None:
        target, action = condition
        event = resolve_hp_threshold_condition(
            sequence, round_number, actor, target, action, setup,
        )
        return event, sequence + 1
    return None, sequence
