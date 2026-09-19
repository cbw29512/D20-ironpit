from __future__ import annotations

import logging

from app.combat.damage_triggered_reactions import resolve_damage_triggered_melee_reaction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _member_by_id(
    setup: EncounterSetup,
    combatant_id: str | None,
) -> EncounterCombatant | None:
    if combatant_id is None:
        return None
    return next(
        (
            member
            for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id == combatant_id
        ),
        None,
    )


def resolve_damage_event_reactions(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
    dice,
    *,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve immediate configured reactions after one completed damage event."""
    try:
        damage_roll = triggering_event.damage_roll
        if damage_roll is None or damage_roll.total <= 0:
            return [], sequence
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError(
                "Damage-trigger dispatch source must match the triggering event actor."
            )

        reactor = _member_by_id(setup, triggering_event.target_id)
        if reactor is None:
            return [], sequence
        reaction = resolve_damage_triggered_melee_reaction(
            sequence,
            round_number,
            reactor,
            source,
            setup,
            dice,
            turn_key=turn_key,
        )
        if reaction is None:
            return [], sequence

        events = [reaction]
        sequence += 1
        follow_up, sequence = resolve_damage_event_reactions(
            sequence,
            round_number,
            reactor,
            reaction,
            setup,
            dice,
            turn_key=turn_key,
        )
        events.extend(follow_up)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Post-damage reaction dispatch failed after event %s.",
            triggering_event.sequence,
        )
        raise RuntimeError("Post-damage reactions could not be resolved.") from exc
