"""Normal post-movement Action selection; mutable state stays on combatants."""
import logging

from app.combat.action_economy import is_available
from app.combat.ally_context import pack_tactics_active
from app.combat.area_weapon_attacks import resolve_area_weapon_attack
from app.combat.attack_actions import resolve_attack_action
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.dodge import resolve_dodge_action
from app.combat.deferred_save_effect import resolve_deferred_save_effect
from app.combat.deferred_save_effect_attack_slot import prefer_deferred_effect_attack_slot
from app.combat.encounter_turn_support import finish_turn, resolve_area_save_turn
from app.combat.intimidating_presence_2014 import resolve_intimidating_presence
from app.combat.hp_threshold_turn import resolve_hp_threshold_turn
from app.combat.landing_offense_policy import decide_post_move_offense
from app.combat.opening_burst import opening_feature_id
from app.combat.multi_target_save_actions import resolve_multi_target_save_action
from app.combat.spell_offense import resolve_best_spell_offense
from app.combat.standard_attack_action import resolve_standard_attack_action

logger = logging.getLogger(__name__)


def resolve_post_move_action(events, sequence, round_number, attacker, target, setup, dice, turn_key):
    """Select the landable Action family under the shared landing-damage rule."""
    try:
        threshold_event, sequence = resolve_hp_threshold_turn(sequence, round_number, attacker, setup, dice)
        if threshold_event is not None:
            events.extend(threshold_event if isinstance(threshold_event, list) else [threshold_event])
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        pick = decide_post_move_offense(attacker, setup, turn_key)
        if pick.family == "spell":
            spell_events, sequence = resolve_best_spell_offense(
                sequence, round_number, attacker, setup, turn_key, dice,
            )
            events.extend(spell_events)
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if pick.family == "presence":
            presence = resolve_intimidating_presence(sequence, round_number, attacker, pick.payload or target, dice)
            if presence is not None:
                events.append(presence)
                sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if pick.family == "multi-save":
            more, sequence = resolve_multi_target_save_action(
                sequence, round_number, attacker, setup, dice, pick.payload,
            )
            events.extend(more)
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        deferred = None if prefer_deferred_effect_attack_slot(attacker, setup) else resolve_deferred_save_effect(
            sequence, round_number, attacker, setup, dice,
        )
        if pick.family not in {"attack-action", "standard-attack", "area-weapon", "area-save", "save-action"} and deferred is not None:
            events.append(deferred)
            sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if pick.family == "area-weapon":
            area_events, sequence = resolve_area_weapon_attack(
                sequence, round_number, attacker, setup, dice, pick.payload,
            )
            events.extend(area_events)
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if pick.family == "attack-action":
            action_events, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
            events.extend(action_events)
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if pick.family == "area-save":
            area_result = resolve_area_save_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
            if area_result is not None:
                return area_result
        if pick.family == "save-action" and is_available(attacker.state, "action"):
            save_target, save_action, distance = pick.payload
            affected = [member.state for member in [*setup.heroes, *setup.monsters]]
            more, sequence = resolve_save_event_chain(
                sequence, round_number, attacker, save_target, save_action, distance, dice, setup,
                turn_key=turn_key, affected_states=affected,
            )
            events.extend(more)
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if pick.family == "standard-attack" and is_available(attacker.state, "action"):
            attack_target, attack, distance = pick.payload
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
    except Exception:
        logger.exception("Post-movement Action resolution failed for %s.", attacker.combatant_id)
        raise
