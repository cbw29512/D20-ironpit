from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_action_rules import preferred_distance, slot_choice, validate_slots
from app.combat.attack_action_targeting import select_slot_target
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_movement import take_encounter_dash
from app.combat.encounter_targeting import combatant_distance
from app.combat.light_attack_resolution import resolve_light_extra_attack
from app.combat.opening_burst import opening_feature_id
from app.combat.reaction_movement import move_toward_with_reactions
from app.combat.saving_throws import resolve_save_action
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)


def _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice, turn_key):
    events, sequence, _ = move_toward_with_reactions(
        sequence, round_number, attacker, target, setup, preferred_distance(attacker, slot), dice,
        turn_key=turn_key,
    )
    return events, sequence


def _prepare_first_slot(sequence, round_number, attacker, target, slot, setup, dice, turn_key):
    if any(slot_choice(attacker, target, slot)):
        return [], sequence, True
    events, sequence = _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice, turn_key)
    if attacker.state.is_dead or attacker.state.is_unconscious:
        return events, sequence, False
    if any(slot_choice(attacker, target, slot)):
        return events, sequence, True
    if not is_available(attacker.state, "action"):
        return events, sequence, False
    events.append(take_encounter_dash(sequence, round_number, attacker, target))
    sequence += 1
    more, sequence = _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice, turn_key)
    events.extend(more)
    return events, sequence, False


def resolve_attack_action(
    sequence: int, round_number: int, attacker: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve an explicit Attack action or monster Multiattack with legal movement and retargeting."""
    try:
        validate_slots(attacker)
        definition = attacker.state.template.attack_action
        if definition is None or not is_available(attacker.state, "action"):
            raise ValueError("Attack action or Multiattack is not available.")
        turn_key = f"{round_number}:{attacker.combatant_id}"
        target = select_slot_target(attacker, setup, definition.slots[0])
        if target is None:
            return [], sequence
        events, sequence, ready = _prepare_first_slot(
            sequence, round_number, attacker, target, definition.slots[0], setup, dice, turn_key,
        )
        if not ready:
            return events, sequence

        spend(attacker.state, "action")
        opening_feature = opening_feature_id(round_number, attacker, setup)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        light_trigger: WeaponAttack | None = None
        for slot in definition.slots:
            if attacker.state.is_dead or attacker.state.is_unconscious:
                break
            target = select_slot_target(attacker, setup, slot)
            if target is None:
                continue
            attack, save_action = slot_choice(attacker, target, slot)
            if attack is None and save_action is None:
                moved, sequence = _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice, turn_key)
                events.extend(moved)
                if attacker.state.is_dead or attacker.state.is_unconscious:
                    break
                attack, save_action = slot_choice(attacker, target, slot)
            if attack is not None:
                pack = pack_tactics_active(attacker, target, setup)
                feature_id = opening_feature or ("pack-tactics" if pack else definition.id)
                events.append(resolve_encounter_attack(
                    sequence, round_number, attacker, target, attack,
                    combatant_distance(attacker, target), dice, setup,
                    spend_action=False, advantage_sources=1 if pack else 0, feature_id=feature_id,
                    turn_key=turn_key, allow_reckless=True,
                ))
                if definition.is_attack_action and light_trigger is None and attack.weapon.light:
                    light_trigger = attack
                opening_feature = None
                sequence += 1
            elif save_action is not None:
                events.append(resolve_save_action(
                    sequence, round_number, attacker, target, save_action,
                    combatant_distance(attacker, target), dice, spend_action=False,
                    affected_states=affected_states,
                ))
                sequence += 1
        if definition.is_attack_action and light_trigger is not None:
            more, sequence = resolve_light_extra_attack(
                sequence, round_number, attacker, setup, dice, light_trigger, turn_key,
            )
            events.extend(more)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Attack action sequence failed for %s.", attacker.combatant_id)
        raise RuntimeError("Attack action sequence could not be resolved.") from exc
