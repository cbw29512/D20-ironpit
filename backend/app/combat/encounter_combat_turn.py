from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_actions import resolve_attack_action
from app.combat.barbarian import enter_rage
from app.combat.charge import resolve_charge_closing
from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.dodge import resolve_dodge_action
from app.combat.encounter_turn_support import finish_turn, resolve_support_actions, save_choice
from app.combat.frightened import frightened_d20_disadvantage
from app.combat.grapple import cleanup_grapples, resolve_escape_grapple, should_escape_grapple
from app.combat.ongoing_spell_control import build_forced_retreat_event, forced_retreat_active
from app.combat.opening_burst import opening_feature_id
from app.combat.offensive_movement_policy import move_to_enable_offense
from app.combat.orc import should_use_adrenaline_rush, use_adrenaline_rush
from app.combat.pit_policy import choose_standard_attack, target_order
from app.combat.policy import should_use_second_wind
from app.combat.recharge import resolve_start_turn_recharges
from app.combat.recharge_action_resolution import resolve_priority_recharge_action
from app.combat.saving_throws import resolve_save_action
from app.combat.spell_offense import resolve_best_spell_offense
from app.combat.standard_attack_action import resolve_standard_attack_action
from app.combat.state import begin_turn
from app.combat.swallow_action_resolution import resolve_priority_swallow_action
from app.combat.tactical_shift import resolve_tactical_shift
from app.combat.fighter import use_second_wind
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_combat_turn(
    sequence: int, round_number: int, attacker: EncounterCombatant, target: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve one Iron Pit turn through shared legality, movement, and fallback policy."""
    try:
        events: list[BattleEvent] = []
        cleanup_grapples(setup)
        begin_turn(attacker.state)
        recharge_events, sequence = resolve_start_turn_recharges(
            sequence, round_number, attacker.combatant_id, attacker.state, dice,
        )
        events.extend(recharge_events)
        turn_key = f"{round_number}:{attacker.combatant_id}"
        if forced_retreat_active(attacker.state):
            events.append(build_forced_retreat_event(sequence, round_number, attacker.combatant_id, attacker.state))
            sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key, allow_surge=False)
        support_events, sequence = resolve_support_actions(sequence, round_number, attacker, setup, dice, turn_key)
        events.extend(support_events)
        if is_incapacitated(attacker.state):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        rage_event = enter_rage(sequence, round_number, attacker.state, attacker.combatant_id)
        if rage_event is not None:
            events.append(rage_event)
            sequence += 1
        if should_use_second_wind(attacker.state):
            events.append(use_second_wind(sequence, round_number, attacker.state, dice, attacker.combatant_id))
            sequence += 1
            shift_event = resolve_tactical_shift(sequence, round_number, attacker, setup)
            if shift_event is not None:
                events.append(shift_event)
                sequence += 1
        if should_escape_grapple(attacker.state):
            events.append(resolve_escape_grapple(sequence, round_number, attacker.combatant_id, attacker.state, dice, other_disadvantage_sources=frightened_d20_disadvantage(attacker.state, setup)))
            sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)
        if should_use_adrenaline_rush(attacker.state):
            adrenaline_event = use_adrenaline_rush(sequence, round_number, attacker.state, attacker.combatant_id)
            if adrenaline_event is not None:
                events.append(adrenaline_event)
                sequence += 1

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
        if charged or attacker.state.is_dead or attacker.state.is_unconscious:
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        movement_events, sequence = move_to_enable_offense(
            sequence, round_number, attacker, setup, turn_key, dice,
        )
        events.extend(movement_events)
        if attacker.state.is_dead or attacker.state.is_unconscious or is_incapacitated(attacker.state):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        spell_events, sequence = resolve_best_spell_offense(sequence, round_number, attacker, setup, turn_key, dice)
        events.extend(spell_events)
        if not is_available(attacker.state, "action"):
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        recharge_action_events, sequence, recharge_handled = resolve_priority_recharge_action(
            sequence, round_number, attacker, setup, dice, turn_key,
        )
        events.extend(recharge_action_events)
        if recharge_handled:
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        swallow_events, sequence, swallow_handled = resolve_priority_swallow_action(
            sequence, round_number, attacker, setup,
        )
        events.extend(swallow_events)
        if swallow_handled:
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        if attacker.state.template.attack_action is not None:
            action_events, sequence = resolve_attack_action(sequence, round_number, attacker, setup, dice)
            events.extend(action_events)
            if action_events or not is_available(attacker.state, "action"):
                return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        chosen_save = save_choice(attacker, setup)
        if chosen_save is not None and is_available(attacker.state, "action"):
            save_target, save_action, distance = chosen_save
            affected = [member.state for member in [*setup.heroes, *setup.monsters]]
            events.append(resolve_save_action(
                sequence, round_number, attacker, save_target, save_action, distance, dice,
                affected_states=affected,
            ))
            sequence += 1
            return finish_turn(events, sequence, round_number, attacker, setup, dice, turn_key)

        attack_choice = choose_standard_attack(attacker, setup)
        if attack_choice is not None and is_available(attacker.state, "action"):
            attack_target, attack, distance = attack_choice
            pack = pack_tactics_active(attacker, attack_target, setup)
            feature = opening_feature_id(round_number, attacker, setup) or ("pack-tactics" if pack else None)
            more, sequence = resolve_standard_attack_action(
                sequence, round_number, attacker, attack_target, attack, distance, dice, setup, turn_key,
                advantage_sources=1 if pack else 0, feature_id=feature,
            )
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