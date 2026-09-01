from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_action_targeting import select_slot_target
from app.combat.attack_legality import attack_allowed_against
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_movement import take_encounter_dash
from app.combat.encounter_targeting import combatant_distance
from app.combat.opening_burst import opening_feature_id
from app.combat.policy import preferred_distance_for_attacks, select_allowed_weapon_attack
from app.combat.reaction_movement import move_toward_with_reactions
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _validate_slots(attacker: EncounterCombatant) -> None:
    definition = attacker.state.template.attack_action
    if definition is None:
        raise ValueError("Combatant has no Multiattack action.")
    attacks = {attacker.state.template.weapon_attack.id, *(a.id for a in attacker.state.template.alternate_weapon_attacks)}
    saves = {action.id for action in attacker.state.template.saving_throw_actions}
    for slot in definition.slots:
        unknown = (set(slot.attack_ids) - attacks) | (set(slot.save_action_ids) - saves)
        if unknown:
            raise ValueError(f"Unknown Multiattack IDs in {definition.name}: {sorted(unknown)}")


def _slot_choice(attacker, target, slot):
    distance = combatant_distance(attacker, target)
    profiles = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
    legal_ids = [
        attack.id for attack in profiles
        if attack.id in slot.attack_ids and attack_allowed_against(attack, attacker.combatant_id, target.state)
    ]
    attack = select_allowed_weapon_attack(attacker.state, distance, legal_ids)
    allowed = set(slot.save_action_ids)
    save = None if attack is not None else next((
        action for action in attacker.state.template.saving_throw_actions
        if action.id in allowed and legal_save_action(action, target, distance)
    ), None)
    return attack, save


def _preferred_distance(attacker: EncounterCombatant, slot: AttackActionSlot) -> int:
    if slot.attack_ids:
        return preferred_distance_for_attacks(attacker.state, slot.attack_ids)
    allowed = set(slot.save_action_ids)
    ranges = [a.range_ft for a in attacker.state.template.saving_throw_actions if a.id in allowed]
    if not ranges:
        raise ValueError("Multiattack slot has no known action range.")
    return max(ranges)


def _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice):
    events, sequence, _ = move_toward_with_reactions(
        sequence, round_number, attacker, target, setup, _preferred_distance(attacker, slot), dice,
    )
    return events, sequence


def _prepare_first_slot(sequence, round_number, attacker, target, slot, setup, dice):
    if any(_slot_choice(attacker, target, slot)):
        return [], sequence, True
    events, sequence = _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice)
    if attacker.state.is_dead or attacker.state.is_unconscious:
        return events, sequence, False
    if any(_slot_choice(attacker, target, slot)):
        return events, sequence, True
    if not is_available(attacker.state, "action"):
        return events, sequence, False
    events.append(take_encounter_dash(sequence, round_number, attacker, target))
    sequence += 1
    more, sequence = _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice)
    events.extend(more)
    return events, sequence, False


def resolve_attack_action(
    sequence: int, round_number: int, attacker: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve ordered Multiattack weapon/save steps with movement, legal retargeting, and Reactions."""
    try:
        _validate_slots(attacker)
        definition = attacker.state.template.attack_action
        if definition is None or not is_available(attacker.state, "action"):
            raise ValueError("Multiattack action is not available.")
        target = select_slot_target(attacker, setup, definition.slots[0])
        if target is None:
            return [], sequence
        events, sequence, ready = _prepare_first_slot(
            sequence, round_number, attacker, target, definition.slots[0], setup, dice,
        )
        if not ready:
            return events, sequence

        spend(attacker.state, "action")
        opening_feature = opening_feature_id(round_number, attacker, setup)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        for slot in definition.slots:
            if attacker.state.is_dead or attacker.state.is_unconscious:
                break
            target = select_slot_target(attacker, setup, slot)
            if target is None:
                continue
            attack, save_action = _slot_choice(attacker, target, slot)
            if attack is None and save_action is None:
                moved, sequence = _move_for_slot(sequence, round_number, attacker, target, slot, setup, dice)
                events.extend(moved)
                if attacker.state.is_dead or attacker.state.is_unconscious:
                    break
                attack, save_action = _slot_choice(attacker, target, slot)
            if attack is not None:
                pack = pack_tactics_active(attacker, target, setup)
                feature_id = opening_feature or ("pack-tactics" if pack else definition.id)
                events.append(resolve_encounter_attack(
                    sequence, round_number, attacker, target, attack,
                    combatant_distance(attacker, target), dice, setup,
                    spend_action=False, advantage_sources=1 if pack else 0, feature_id=feature_id,
                ))
                opening_feature = None
                sequence += 1
            elif save_action is not None:
                events.append(resolve_save_action(
                    sequence, round_number, attacker, target, save_action,
                    combatant_distance(attacker, target), dice, spend_action=False,
                    affected_states=affected_states,
                ))
                sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Multiattack sequence failed for %s.", attacker.combatant_id)
        raise RuntimeError("Multiattack sequence could not be resolved.") from exc
