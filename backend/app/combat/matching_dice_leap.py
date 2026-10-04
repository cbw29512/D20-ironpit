from __future__ import annotations

import logging
from collections import Counter

from app.combat.barrier_line_of_effect import clear_line_between_members
from app.combat.damage_reaction_events import damage_event_chain
from app.combat.encounter_targeting import combatant_distance
from app.combat.pit_policy import target_order
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.spell_cast_modifiers import ResourceBackedSpellRangeModifier
from app.domain.spells import SpellAttackAction

logger = logging.getLogger(__name__)


def matching_spell_damage_faces(event: BattleEvent, spell: SpellAttackAction) -> bool:
    try:
        if not event.hit:
            return False
        own = next((part for part in event.damage_components if part.source == spell.name), None)
        if own is None or len(own.rolls) < 2:
            return False
        return any(count >= 2 for count in Counter(own.rolls).values())
    except Exception:
        logger.exception("Failed matching-dice check for %s.", spell.id)
        raise


def choose_leap_target(
    caster: EncounterCombatant,
    origin: EncounterCombatant,
    setup: EncounterSetup,
    range_ft: int,
    excluded_ids: set[str],
) -> EncounterCombatant | None:
    try:
        for candidate in target_order(caster, setup):
            if candidate.combatant_id in excluded_ids:
                continue
            if not candidate.state.is_alive or candidate.state.is_dead or candidate.state.current_hp <= 0:
                continue
            if combatant_distance(origin, candidate) > range_ft:
                continue
            if not clear_line_between_members(origin, candidate, setup):
                continue
            return candidate
        return None
    except Exception:
        logger.exception("Failed to choose a matching-dice leap target from %s.", origin.combatant_id)
        raise


def resolve_matching_dice_leaps(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    origin: EncounterCombatant,
    last_event: BattleEvent,
    spell: SpellAttackAction,
    setup: EncounterSetup,
    turn_key: str,
    dice,
    *,
    slot_level: int,
    range_modifier: ResourceBackedSpellRangeModifier | None = None,
) -> tuple[list[BattleEvent], int]:
    """After a hit, leap to a new creature within range when two or more damage dice match."""
    try:
        range_ft = spell.matching_dice_leap_range_ft
        if range_ft <= 0:
            return [], sequence
        max_leaps = slot_level if slot_level > 0 else spell.level
        excluded = {last_event.target_id} if last_event.target_id else set()
        events: list[BattleEvent] = []
        current_origin = origin
        current_event = last_event
        leaps = 0
        while leaps < max_leaps:
            if not matching_spell_damage_faces(current_event, spell):
                break
            target = choose_leap_target(caster, current_origin, setup, range_ft, excluded)
            if target is None:
                break
            event = resolve_spell_attack(
                sequence,
                round_number,
                caster,
                target,
                spell,
                setup,
                turn_key,
                dice,
                range_modifier=range_modifier,
                cast_slot_level=slot_level if spell.level > 0 else None,
                spend_cast_costs=False,
                skip_range_check=True,
            )
            chain, sequence = damage_event_chain(
                sequence + 1,
                round_number,
                caster,
                event,
                setup,
                dice,
                turn_key=turn_key,
            )
            events.extend(chain)
            leaps += 1
            excluded.add(target.combatant_id)
            current_origin = target
            current_event = event
        return events, sequence
    except Exception:
        logger.exception("Matching-dice leap failed for %s using %s.", caster.combatant_id, spell.id)
        raise
