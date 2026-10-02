from __future__ import annotations

import logging

from app.combat.attack_damage_redirect import resolve_attack_damage_zero_redirect
from app.combat.damage_event_context import applied_damage_total, _member_by_id
from app.combat.hit_rider_events import resolve_hit_rider_event
from app.combat.damage_reaction_dispatch import resolve_damage_reaction_attack
from app.combat.source_zero_hp_triggers import resolve_source_zero_hp_triggers
from app.combat.source_damage_triggers import resolve_source_damage_temporary_hp
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


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
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Damage reaction source must match the triggering event actor.")
        hit_events, sequence = resolve_hit_rider_event(
            sequence, round_number, source, triggering_event, setup, dice, turn_key,
        )
        source_events, sequence = resolve_source_zero_hp_triggers(
            sequence, round_number, source, triggering_event, setup,
        )
        source_events = [*hit_events, *source_events]
        applied_damage = applied_damage_total(triggering_event)
        damage_events, sequence = resolve_source_damage_temporary_hp(
            sequence, round_number, source, triggering_event, applied_damage,
        )
        source_events.extend(damage_events)
        redirect = resolve_attack_damage_zero_redirect(
            sequence, round_number, source, triggering_event, setup, dice,
        )
        if redirect is not None:
            source_events.append(redirect)
            nested, sequence = resolve_damage_event_reactions(
                sequence + 1,
                round_number,
                _member_by_id(setup, redirect.actor_id),
                redirect,
                setup,
                dice,
                turn_key=turn_key,
            )
            source_events.extend(nested)
        if applied_damage <= 0:
            return source_events, sequence

        reactor = _member_by_id(setup, triggering_event.target_id)
        if reactor is None or reactor.combatant_id == source.combatant_id:
            return source_events, sequence

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
            return source_events, sequence

        events = [*source_events, reaction]
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
    try:
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
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Damage event-chain assembly failed: source=%s event=%s next_sequence=%s.",
            source.combatant_id,
            event.sequence,
            next_sequence,
        )
        raise RuntimeError("Damage event chain could not be assembled.") from exc
