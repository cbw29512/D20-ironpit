from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.ally_context import pack_tactics_active
from app.combat.area_weapon_attacks import choose_area_weapon_attack, resolve_area_weapon_attack
from app.combat.attack_actions import resolve_attack_action
from app.combat.charge import resolve_charge_closing
from app.combat.condition_rules import is_incapacitated
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.dice import DiceProvider
from app.combat.dodge import resolve_dodge_action
from app.combat.deferred_save_effect import resolve_deferred_save_effect
from app.combat.encounter_turn_support import finish_turn, resolve_area_save_turn, save_choice
from app.combat.encounter_turn_opening import resolve_turn_opening
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.intimidating_presence_2014 import resolve_intimidating_presence
from app.combat.hp_threshold_turn import resolve_hp_threshold_turn
from app.combat.opening_burst import opening_feature_id
from app.combat.offensive_movement_policy import move_to_enable_offense
from app.combat.paladin_auras_2014 import sync_paladin_auras_2014
from app.combat.persistent_spell_attacks import resolve_persistent_spell_attack
from app.combat.replacement_form_policy import resolve_replacement_form_setup
from app.combat.pit_policy import choose_standard_attack, target_order
from app.combat.spell_offense import resolve_best_spell_offense
from app.combat.standard_attack_action import resolve_standard_attack_action
from app.combat.targeted_concentration_damage import resolve_targeted_concentration_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
logger = logging.getLogger(__name__)

def resolve_combat_turn(
    sequence: int, round_number: int, attacker: EncounterCombatant, target: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve one Iron Pit turn through shared legality, movement, and fallback policy."""
    try:
        events, sequence, turn_key, finish_now, allow_surge = resolve_turn_opening(
            sequence, round_number, attacker, setup, dice,
        )
        if finish_now:
            return finish_turn(
                events, sequence, round_number, attacker, setup, dice, turn_key,
                allow_surge=allow_surge,
            )

        targeted_damage_event = resolve_targeted_concentration_damage(
            sequence, round_number, attacker, setup, turn_key,
        )
        if targeted_damage_event is not None:
            events.append(targeted_damage_event)
            sequence += 1

        persistent_spell_event = resolve_persistent_spell_attack(
            sequence, round_number, attacker, setup, turn_key, dice,
        )
        if persistent_spell_event is not None:
            events.append(persistent_spell_event)
            sequence += 1

        form_events, sequence = resolve_replacement_form_setup(
            sequence, round_number, attacker, setup, turn_key, dice,
        )
        events.extend(form_events)
        if not is_available(attacker.state, "action"):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        spell_events, sequence = resolve_best_spell_offense(sequence, round_number, attacker, setup, turn_key, dice)
        events.extend(spell_events)
        if not is_available(attacker.state, "action"):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        targets = target_order(attacker, setup)
        if not targets:
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        charge_events, sequence, charged = resolve_charge_closing(
            sequence, round_number, attacker, targets[0], dice, setup,
        )
        events.extend(charge_events)
        if charged:
            sync_paladin_auras_2014(setup)
            sync_friendly_save_auras(setup)
        if charged or attacker.state.is_dead or attacker.state.is_unconscious:
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        movement_events, sequence = move_to_enable_offense(sequence, round_number, attacker, setup, turn_key, dice)
        events.extend(movement_events)
        sync_paladin_auras_2014(setup)
        sync_friendly_save_auras(setup)
        if attacker.state.is_dead or attacker.state.is_unconscious or is_incapacitated(attacker.state):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        spell_events, sequence = resolve_best_spell_offense(sequence, round_number, attacker, setup, turn_key, dice)
        events.extend(spell_events)
        if not is_available(attacker.state, "action"):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        presence = resolve_intimidating_presence(sequence, round_number, attacker, target, dice)
        if presence is not None:
            events.append(presence); sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        threshold_event, sequence = resolve_hp_threshold_turn(sequence, round_number, attacker, setup)
        if threshold_event is not None:
            events.append(threshold_event)
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        deferred = resolve_deferred_save_effect(sequence, round_number, attacker, setup, dice)
        if deferred is not None:
            events.append(deferred); sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        area_weapon = choose_area_weapon_attack(attacker, setup)
        if area_weapon is not None:
            area_events, sequence = resolve_area_weapon_attack(
                sequence, round_number, attacker, setup, dice, area_weapon,
            )
            events.extend(area_events)
            if area_events or not is_available(attacker.state, "action"):
                return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        if attacker.state.template.attack_action is not None:
            action_events, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
            events.extend(action_events)
            if action_events or not is_available(attacker.state, "action"):
                return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        area_result = resolve_area_save_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if area_result is not None:
            return area_result

        chosen_save = save_choice(attacker, setup)
        if chosen_save is not None and is_available(attacker.state, "action"):
            save_target, save_action, distance = chosen_save
            affected = [member.state for member in [*setup.heroes, *setup.monsters]]
            more, sequence = resolve_save_event_chain(
                sequence, round_number, attacker, save_target, save_action, distance, dice, setup,
                turn_key=turn_key, affected_states=affected,
            )
            events.extend(more)
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        attack_choice = choose_standard_attack(attacker, setup)
        if attack_choice is not None and is_available(attacker.state, "action"):
            attack_target, attack, distance = attack_choice
            pack = pack_tactics_active(attacker, attack_target, setup)
            feature = opening_feature_id(round_number, attacker, setup) or ("pack-tactics" if pack else None)
            more, sequence = resolve_standard_attack_action(
                sequence, round_number, attacker, attack_target, attack, distance, dice, setup, turn_key,
                advantage_sources=1 if pack else 0, feature_id=feature)
            events.extend(more)
        elif is_available(attacker.state, "action"):
            events.append(resolve_dodge_action(sequence, round_number, attacker))
            sequence += 1
        return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Combat-turn resolution failed for %s.", attacker.combatant_id)
        raise RuntimeError("Combat turn could not be resolved.") from exc
