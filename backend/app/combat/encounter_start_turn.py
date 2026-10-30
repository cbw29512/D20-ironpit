from __future__ import annotations

import logging

from app.combat.attachments import resolve_attachment_start_turn
from app.combat.auras import resolve_start_turn_grapple_contact_damage
from app.combat.bloodied_berserk import resolve_start_turn_berserk
from app.combat.concentration import end_concentration_if_expired
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.grapple import cleanup_grapples
from app.combat.grapple_periodic_damage import resolve_grapple_periodic_damage
from app.combat.progression_recovery import resolve_bloodied_start_turn_healing
from app.combat.regeneration import resolve_start_turn_regeneration
from app.combat.start_turn_auras import resolve_start_turn_save_condition_auras
from app.combat.state import refresh_start_of_turn
from app.combat.timed_conditions import expire_start_of_turn_conditions

logger = logging.getLogger(__name__)


def resolve_start_turn_lifecycle(
    sequence,
    round_number,
    member,
    setup,
    dice,
    affected_states,
):
    """Resolve shared owner/target start-turn lifecycle before the acting turn."""
    try:
        events = []
        refresh_start_of_turn(member.state)

        berserk_event, sequence = resolve_start_turn_berserk(
            sequence, round_number, member, dice,
        )
        if berserk_event is not None:
            events.append(berserk_event)

        cleanup_grapples(setup)
        periodic_events, sequence = resolve_grapple_periodic_damage(
            sequence, round_number, member, setup, dice,
        )
        events.extend(periodic_events)

        contact_events, sequence = resolve_start_turn_grapple_contact_damage(
            sequence, round_number, member, setup, dice,
        )
        events.extend(contact_events)

        resolve_start_turn_regeneration(member.state)
        resolve_bloodied_start_turn_healing(member.state)
        end_concentration_if_expired(member.state, round_number, affected_states)

        expiry_events, sequence = expire_start_of_turn_conditions(
            sequence, round_number, member, setup,
        )
        events.extend(expiry_events)

        lifecycle_events, sequence = resolve_target_condition_timing(
            sequence, round_number, member, "target_turn_start", dice,
        )
        events.extend(lifecycle_events)

        aura_events, sequence = resolve_start_turn_save_condition_auras(
            sequence, round_number, member, setup, dice,
        )
        events.extend(aura_events)

        attachment_events, sequence = resolve_attachment_start_turn(
            sequence, round_number, member, setup, dice,
        )
        events.extend(attachment_events)
        return events, sequence
    except Exception as exc:
        logger.exception("Failed start-turn lifecycle for %s.", member.combatant_id)
        raise RuntimeError("Start-turn lifecycle failed.") from exc
