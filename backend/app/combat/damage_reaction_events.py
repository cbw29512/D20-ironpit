from __future__ import annotations

import logging

from app.combat.damage_reaction_dispatch import resolve_damage_reaction_attack
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def applied_damage_total(event: BattleEvent) -> int:
    """Measure damage actually applied after defenses and Temporary HP."""
    try:
        components = list(event.damage_components)
        if components and all(part.applied_total is not None for part in components):
            return sum(int(part.applied_total or 0) for part in components)

        hp_known = event.hp_before is not None and event.hp_after is not None
        temporary_hp_known = (
            event.temporary_hp_before is not None and event.temporary_hp_after is not None
        )
        hp_loss = max(0, event.hp_before - event.hp_after) if hp_known else 0
        temporary_hp_loss = (
            max(0, event.temporary_hp_before - event.temporary_hp_after)
            if temporary_hp_known
            else 0
        )
        # Snapshot state is authoritative even when it proves that zero damage landed.
        # Falling through to the raw damage roll here would incorrectly trigger reactions
        # after immunity, absorption, or another defense reduced applied damage to zero.
        if hp_known or temporary_hp_known:
            return hp_loss + temporary_hp_loss
        return max(0, event.damage_roll.total) if event.damage_roll is not None else 0
    except Exception as exc:
        logger.exception("Failed to measure applied damage for event %s.", event.sequence)
        raise RuntimeError("Applied damage could not be measured.") from exc


def _member_by_id(setup: EncounterSetup, combatant_id: str | None) -> EncounterCombatant | None:
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
    dice: DiceProvider,
    *,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve immediate legal reactions after one completed creature-damage event."""
    try:
        applied_damage = applied_damage_total(triggering_event)
        if applied_damage <= 0:
            return [], sequence
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Damage reaction source must match the triggering event actor.")

        reactor = _member_by_id(setup, triggering_event.target_id)
        if reactor is None or reactor.combatant_id == source.combatant_id:
            return [], sequence

        reaction = resolve_damage_reaction_attack(
            sequence,
            round_number,
            reactor,
            source,
            setup,
            applied_damage,
            dice,
            turn_key=turn_key,
        )
        if reaction is None:
            return [], sequence

        events = [reaction]
        nested, next_sequence = resolve_damage_event_reactions(
            sequence + 1,
            round_number,
            reactor,
            reaction,
            setup,
            dice,
            turn_key=turn_key,
        )
        events.extend(nested)
        return events, next_sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Post-damage reaction dispatch failed after event %s.",
            triggering_event.sequence,
        )
        raise RuntimeError("Post-damage reactions could not be resolved.") from exc


def damage_event_chain(
    next_sequence: int,
    round_number: int,
    source: EncounterCombatant,
    event: BattleEvent,
    setup: EncounterSetup,
    dice: DiceProvider,
    *,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    """Return one resolved damage event followed by any immediate reaction chain."""
    reactions, final_sequence = resolve_damage_event_reactions(
        next_sequence,
        round_number,
        source,
        event,
        setup,
        dice,
        turn_key=turn_key,
    )
    return [event, *reactions], final_sequence
