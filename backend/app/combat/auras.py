from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.ongoing_damage import encounter_members, resolve_ongoing_damage
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.save_effects import PeriodicDamageEffectDefinition

logger = logging.getLogger(__name__)


def _apply_pit_ignition(
    target: EncounterCombatant,
    source: EncounterCombatant,
    aura_id: str,
    round_number: int,
) -> str | None:
    try:
        effect_id = "burn" + "ing"
        if any(effect.effect_id == effect_id for effect in target.state.timed_effects):
            return effect_id
        return apply_timed_condition(
            target.state,
            effect_id,
            source.combatant_id,
            source_effect_id=aura_id,
            applied_round=round_number,
            periodic_damage=PeriodicDamageEffectDefinition(
                timing="target_turn_end",
                dice_count=1,
                dice_size=6,
                damage_bonus=0,
                damage_type="fire",
            ),
        )
    except Exception as exc:
        logger.exception("Failed Pit ignition application for %s.", target.combatant_id)
        raise RuntimeError("Pit ignition effect could not be applied.") from exc


def resolve_end_turn_damage_auras(
    sequence: int, round_number: int, source: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-defined damaging emanations at the owner's end-turn timing window."""
    try:
        events: list[BattleEvent] = []
        if source.state.is_dead or not source.state.is_alive:
            return events, sequence
        for aura in source.state.template.end_turn_damage_auras:
            if aura.disabled_while_incapacitated and is_incapacitated(source.state):
                continue
            targets = [
                member for member in encounter_members(setup)
                if member.side != source.side and member.state.is_alive and not member.state.is_dead
                and combatant_distance(source, member) <= aura.radius_ft
            ]
            for target in targets:
                event = resolve_ongoing_damage(
                    sequence, round_number, source, target, setup, dice,
                    feature_id=aura.id, feature_name=aura.name,
                    dice_count=aura.damage_dice_count, dice_size=aura.damage_dice_size,
                    damage_bonus=aura.damage_bonus, damage_type=aura.damage_type,
                    animation="aura-damage",
                )
                if aura.applies_burning and target.state.is_alive and not target.state.is_dead:
                    applied = _apply_pit_ignition(target, source, aura.id, round_number)
                    if applied and applied not in event.applied_condition_ids:
                        event.applied_condition_ids.append(applied)
                events.append(event)
                sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Failed end-turn aura resolution for %s.", source.combatant_id)
        raise RuntimeError("End-turn aura resolution failed.") from exc


def resolve_start_turn_grapple_contact_damage(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve owner-turn damage against every creature in an active grapple link."""
    try:
        profile = source.state.template.start_turn_grapple_contact_damage
        if profile is None or source.state.is_dead or not source.state.is_alive:
            return [], sequence

        members = encounter_members(setup)
        by_id = {member.combatant_id: member for member in members}
        target_ids = {
            grapple.source_id
            for grapple in source.state.grapple_sources
            if grapple.source_id in by_id
        }
        target_ids.update(
            member.combatant_id
            for member in members
            if member.combatant_id != source.combatant_id
            and any(
                grapple.source_id == source.combatant_id
                for grapple in member.state.grapple_sources
            )
        )

        events: list[BattleEvent] = []
        for target_id in sorted(target_ids):
            target = by_id[target_id]
            if target.state.is_dead or not target.state.is_alive:
                continue
            events.append(resolve_ongoing_damage(
                sequence,
                round_number,
                source,
                target,
                setup,
                dice,
                feature_id=profile.id,
                feature_name=profile.name,
                dice_count=profile.damage_dice_count,
                dice_size=profile.damage_dice_size,
                damage_bonus=profile.damage_bonus,
                damage_type=profile.damage_type,
                animation="grapple-contact-damage",
            ))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Failed grapple-contact damage resolution for %s.", source.combatant_id)
        raise RuntimeError("Grapple-contact damage resolution failed.") from exc
