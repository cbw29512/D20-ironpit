from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_action_choices import attack_choice, save_choice, followup_target
from app.combat.attack_action_sequences import select_sequence, expanded_sequence_slots
from app.combat.attack_action_event_target import event_target
from app.combat.attack_action_rules import validate_attack_action_slots
from app.combat.attack_action_weapon_buffs import resolve_attack_action_weapon_buff
from app.combat.cleave import resolve_cleave_extra_attack
from app.combat.condition_rules import is_incapacitated
from app.combat.damage_reaction_events import resolve_damage_event_reactions
from app.combat.deferred_save_effect_attack_slot import resolve_deferred_effect_attack_slot
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.light_attack_resolution import resolve_light_extra_attack
from app.combat.opening_burst import opening_feature_id
from app.combat.saving_throws import resolve_save_action
from app.combat.stunning_strike_2014 import resolve_stunning_strike
from app.combat.timed_attack_cap import turn_attack_allowed
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack
from app.domain.event_support import AuditPhase, AuditStep, EventAudit

logger = logging.getLogger(__name__)

def resolve_attack_action(
    sequence: int, round_number: int, attacker: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve Multiattack/Extra Attack against currently legal battlefield targets."""
    try:
        validate_attack_action_slots(attacker)
        definition = attacker.state.template.attack_action
        if definition is None or not is_available(attacker.state, "action"):
            raise ValueError("Attack action or Multiattack is not available.")
        selected = select_sequence(attacker, setup)
        if selected is None:
            return [], sequence

        spend(attacker.state, "action")
        variant, mode = selected
        slots, repetition_roll = expanded_sequence_slots(variant, dice)
        events: list[BattleEvent] = []
        if repetition_roll is not None:
            events.append(BattleEvent(sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
                feature_id=variant.id, feature_roll=repetition_roll, animation="feature",
                description=f"{attacker.state.template.name}: {definition.name} rolls {repetition_roll.notation} = {repetition_roll.total}.",
                audit=EventAudit(steps=[AuditStep(phase=AuditPhase.ROLL, kind="roll", label="Printed sequence repetition")]))
            )
            sequence += 1
        attack_buff = resolve_attack_action_weapon_buff(
            sequence,
            round_number,
            attacker,
        )
        if attack_buff is not None:
            events.append(attack_buff)
            sequence += 1
        opening_feature = opening_feature_id(round_number, attacker, setup)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        light_trigger: WeaponAttack | None = None
        turn_key = f"{round_number}:{attacker.combatant_id}"

        previous_attack = None
        for index, slot in enumerate(slots):
            if attacker.state.is_dead or attacker.state.is_unconscious or attacker.state.turn_terminated:
                break
            eligible, target_id = followup_target(slot, previous_attack.hit if previous_attack and previous_attack.event_type == "attack" else None,
                                                 previous_attack.target_id if previous_attack else None)
            previous_attack = None
            if not eligible:
                continue
            deferred = resolve_deferred_effect_attack_slot(
                sequence,
                round_number,
                attacker,
                setup,
                dice,
            )
            if deferred is not None:
                events.append(deferred)
                sequence += 1
                opening_feature = None
                continue
            chosen_attack = attack_choice(attacker, setup, slot, mode=mode, target_id=target_id)
            if chosen_attack is not None:
                if not turn_attack_allowed(attacker.state):
                    break
                target, attack, distance = chosen_attack
                pack = pack_tactics_active(attacker, target, setup)
                feature_id = opening_feature or ("pack-tactics" if pack else variant.id)
                event = resolve_encounter_attack(
                    sequence, round_number, attacker, target, attack, distance, dice, setup,
                    spend_action=False, advantage_sources=1 if pack else 0,
                    feature_id=feature_id, turn_key=turn_key, allow_reckless=True,
                    close_enemy_active=False,
                )
                events.append(event)
                previous_attack = event
                sequence += 1
                if event.hit:
                    actual_target = event_target(event, setup) or target
                    stun = resolve_stunning_strike(
                        sequence,
                        round_number,
                        attacker,
                        actual_target,
                        attack,
                        dice,
                        affected_states=affected_states,
                    )
                    if stun is not None:
                        events.append(stun)
                        sequence += 1
                reactions, sequence = resolve_damage_event_reactions(
                    sequence, round_number, attacker, event, setup, dice, turn_key=turn_key,
                )
                events.extend(reactions)
                if attacker.state.turn_terminated or attacker.state.is_dead or is_incapacitated(attacker.state):
                    break
                cleave, sequence = resolve_cleave_extra_attack(
                    sequence, round_number, attacker, event, attack, setup, dice, turn_key,
                )
                events.extend(cleave)
                if attacker.state.is_dead or is_incapacitated(attacker.state):
                    break
                if definition.is_attack_action and light_trigger is None and attack.weapon.light:
                    light_trigger = attack
                opening_feature = None
                continue

            chosen_save = save_choice(attacker, setup, slot)
            if chosen_save is not None:
                target, save_action, distance = chosen_save
                event = resolve_save_action(
                    sequence, round_number, attacker, target, save_action,
                    distance,
                    dice,
                    spend_action=False,
                    affected_states=affected_states,
                    setup=setup,
                )
                events.append(event)
                sequence += 1
                reactions, sequence = resolve_damage_event_reactions(
                    sequence, round_number, attacker, event, setup, dice, turn_key=turn_key,
                )
                events.extend(reactions)
                if attacker.state.is_dead or is_incapacitated(attacker.state):
                    break

        if (
            definition.is_attack_action and light_trigger is not None
            and not attacker.state.turn_terminated and not attacker.state.is_dead
            and not is_incapacitated(attacker.state)
        ):
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
