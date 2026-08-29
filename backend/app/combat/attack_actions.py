from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_movement import move_toward_combatant, take_encounter_dash
from app.combat.encounter_targeting import combatant_distance, select_nearest_target
from app.combat.policy import preferred_distance_for_attacks, select_allowed_weapon_attack
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction

logger = logging.getLogger(__name__)


def _validate_slots(attacker: EncounterCombatant) -> None:
    definition = attacker.state.template.attack_action
    if definition is None:
        raise ValueError("Combatant has no Multiattack action.")
    known_attacks = {
        attacker.state.template.weapon_attack.id,
        *(attack.id for attack in attacker.state.template.alternate_weapon_attacks),
    }
    known_saves = {action.id for action in attacker.state.template.saving_throw_actions}
    for slot in definition.slots:
        unknown = (set(slot.attack_ids) - known_attacks) | (set(slot.save_action_ids) - known_saves)
        if unknown:
            raise ValueError(f"Unknown Multiattack IDs in {definition.name}: {sorted(unknown)}")


def _save_choice(attacker, target, slot, distance):
    allowed = set(slot.save_action_ids)
    return next((action for action in attacker.state.template.saving_throw_actions
                 if action.id in allowed and legal_save_action(action, target, distance)), None)


def _slot_choice(attacker, target, slot):
    distance = combatant_distance(attacker, target)
    attack = select_allowed_weapon_attack(attacker.state, distance, slot.attack_ids)
    return attack, None if attack is not None else _save_choice(attacker, target, slot, distance)


def _preferred_distance(attacker: EncounterCombatant, slot: AttackActionSlot) -> int:
    if slot.attack_ids:
        return preferred_distance_for_attacks(attacker.state, slot.attack_ids)
    allowed = set(slot.save_action_ids)
    ranges = [action.range_ft for action in attacker.state.template.saving_throw_actions if action.id in allowed]
    if not ranges:
        raise ValueError("Multiattack slot has no known action range.")
    return max(ranges)


def _move_for_slot(sequence, round_number, attacker, target, slot):
    movement = move_toward_combatant(sequence, round_number, attacker, target, _preferred_distance(attacker, slot))
    return ([movement], sequence + 1) if movement is not None else ([], sequence)


def _prepare_first_slot(sequence, round_number, attacker, target, slot):
    if any(_slot_choice(attacker, target, slot)):
        return [], sequence, True
    events, sequence = _move_for_slot(sequence, round_number, attacker, target, slot)
    if any(_slot_choice(attacker, target, slot)):
        return events, sequence, True
    if not is_available(attacker.state, "action"):
        return events, sequence, False
    events.append(take_encounter_dash(sequence, round_number, attacker, target))
    sequence += 1
    more, sequence = _move_for_slot(sequence, round_number, attacker, target, slot)
    events.extend(more)
    return events, sequence, False


def resolve_attack_action(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve ordered Multiattack weapon/save steps with movement and retargeting."""
    try:
        _validate_slots(attacker)
        definition = attacker.state.template.attack_action
        if definition is None or not is_available(attacker.state, "action"):
            raise ValueError("Multiattack action is not available.")
        target = select_nearest_target(attacker, setup)
        if target is None:
            return [], sequence
        events, sequence, ready = _prepare_first_slot(sequence, round_number, attacker, target, definition.slots[0])
        if not ready:
            return events, sequence

        spend(attacker.state, "action")
        for slot in definition.slots:
            target = select_nearest_target(attacker, setup)
            if target is None:
                break
            attack, save_action = _slot_choice(attacker, target, slot)
            if attack is None and save_action is None:
                movement, sequence = _move_for_slot(sequence, round_number, attacker, target, slot)
                events.extend(movement)
                attack, save_action = _slot_choice(attacker, target, slot)
            if attack is not None:
                pack = pack_tactics_active(attacker, target, setup)
                events.append(resolve_attack(
                    sequence, round_number, attacker.state, target.state, attack,
                    combatant_distance(attacker, target), dice,
                    actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
                    spend_action=False, advantage_sources=1 if pack else 0,
                    feature_id="pack-tactics" if pack else definition.id,
                ))
                sequence += 1
            elif save_action is not None:
                events.append(resolve_save_action(
                    sequence, round_number, attacker, target, save_action,
                    combatant_distance(attacker, target), dice, spend_action=False,
                ))
                sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Multiattack sequence failed for %s.", attacker.combatant_id)
        raise RuntimeError("Multiattack sequence could not be resolved.") from exc
