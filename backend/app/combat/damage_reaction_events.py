from __future__ import annotations

import logging

from app.combat.damage_reaction_dispatch import resolve_damage_reaction_attack
from app.combat.dice import DiceProvider
from app.combat.temporary_hp import grant_temporary_hit_points
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
    try:
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
    except Exception as exc:
        logger.exception("Failed to resolve encounter member %s for damage reaction.", combatant_id)
        raise RuntimeError("Damage reaction encounter member could not be resolved.") from exc


def resolve_source_zero_hp_triggers(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-owned effects triggered by reducing a hostile creature to 0 HP."""
    try:
        rule = source.state.template.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp
        if rule is None:
            return [], sequence
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Zero-HP trigger source must match the triggering event actor.")
        target = _member_by_id(setup, triggering_event.target_id)
        if target is None or target.combatant_id == source.combatant_id or target.side == source.side:
            return [], sequence
        if triggering_event.hp_before is None or triggering_event.hp_after is None:
            return [], sequence
        if triggering_event.hp_before <= 0 or triggering_event.hp_after != 0:
            return [], sequence
        scores = source.state.template.ability_scores
        level = source.state.template.level
        if scores is None or level is None:
            raise ValueError("Zero-HP Temporary HP trigger requires certified ability scores and level.")
        amount = max(
            rule.minimum,
            rule.flat_bonus + rule.per_level * level + scores.modifier(rule.ability),
        )
        before = source.state.temporary_hp
        after = grant_temporary_hit_points(source.state, amount)
        return [BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=source.combatant_id,
            actor_name=source.state.template.name,
            target_id=source.combatant_id,
            target_name=source.state.template.name,
            hp_before=source.state.current_hp,
            hp_after=source.state.current_hp,
            temporary_hp_before=before,
            temporary_hp_after=after,
            feature_id=rule.source_id,
            animation="feature",
            description=(
                f"{source.state.template.name} gains {amount} Temporary HP from {rule.source_name} "
                f"after reducing a hostile creature to 0 HP."
            ),
        )], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Source zero-HP trigger dispatch failed after event %s.", triggering_event.sequence)
        raise RuntimeError("Source zero-HP trigger could not be resolved.") from exc


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
        source_events, sequence = resolve_source_zero_hp_triggers(
            sequence, round_number, source, triggering_event, setup,
        )
        applied_damage = applied_damage_total(triggering_event)
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
