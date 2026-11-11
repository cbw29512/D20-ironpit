"""Turn one legal barrier placement into existing cast/save/damage events."""
from __future__ import annotations

import logging

from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.encounter_targeting import combatant_distance
from app.combat.persistent_barrier_cast import cast_persistent_barrier

logger = logging.getLogger(__name__)

def resolve_offensive_barrier(sequence, round_number, actor, setup, dice, turn_key, choice):
    """Reuse ordinary barrier cast and save-event/reaction chains, no special damage."""
    try:
        event, sequence = cast_persistent_barrier(
            sequence, round_number, actor, setup, choice.action,
            [list(panel) for panel in choice.sections], turn_key,
        )
        event.description += " Arena forced displacement is logged without moving targets."
        events = [event]
        index = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        for target_id in choice.affected_ids:
            target = index[target_id]
            if target.state.is_dead or not target.state.is_alive:
                continue
            damage, sequence = resolve_save_event_chain(
                sequence, round_number, actor, target, choice.action.on_creation_save,
                combatant_distance(actor, target), dice, setup, turn_key=turn_key,
                spend_action=False, check_resource=False, spend_resource=False,
                affected_states=[member.state for member in index.values()],
            )
            events.extend(damage)
        return events, sequence
    except Exception:
        logger.exception("Offensive barrier cast failed for %s", actor.combatant_id)
        raise
