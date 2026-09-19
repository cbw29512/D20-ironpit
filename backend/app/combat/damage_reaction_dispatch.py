from __future__ import annotations

import logging

from app.combat.damage_triggered_reactions import resolve_damage_triggered_melee_reaction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def applied_damage_total(event: BattleEvent) -> int:
    """Return damage actually applied after defenses, including Temporary HP."""
    try:
        components = list(event.damage_components)
        if components and all(part.applied_total is not None for part in components):
            return sum(int(part.applied_total or 0) for part in components)
        hp_loss = (
            max(0, event.hp_before - event.hp_after)
            if event.hp_before is not None and event.hp_after is not None else 0
        )
        temp_loss = (
            max(0, event.temporary_hp_before - event.temporary_hp_after)
            if event.temporary_hp_before is not None and event.temporary_hp_after is not None else 0
        )
        if hp_loss or temp_loss:
            return hp_loss + temp_loss
        return max(0, event.damage_roll.total) if event.damage_roll is not None else 0
    except Exception as exc:
        logger.exception("Failed to measure applied damage for event %s.", event.sequence)
        raise RuntimeError("Applied damage could not be measured.") from exc


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
        if applied_damage_total(triggering_event) <= 0:
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


def append_event_with_damage_reactions(
    events: list[BattleEvent],
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    event: BattleEvent,
    setup: EncounterSetup,
    dice,
    *,
    turn_key: str | None = None,
) -> int:
    """Append one event and any immediate damage-triggered reaction events."""
    events.append(event)
    reactions, sequence = resolve_damage_event_reactions(
        sequence,
        round_number,
        source,
        event,
        setup,
        dice,
        turn_key=turn_key,
    )
    events.extend(reactions)
    return sequence
