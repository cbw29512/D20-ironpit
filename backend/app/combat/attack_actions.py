from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_action_choices import attack_choice, save_choice, slot_has_legal_choice, use_ranged_split
from app.combat.attack_action_rules import validate_attack_action_slots
from app.combat.cleave import resolve_cleave_extra_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.light_attack_resolution import resolve_light_extra_attack
from app.combat.opening_burst import opening_feature_id
from app.combat.pit_policy import flexible_slot_has_both
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

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
        if not any(slot_has_legal_choice(attacker, setup, slot) for slot in definition.slots):
            return [], sequence

        spend(attacker.state, "action")
        events: list[BattleEvent] = []
        opening_feature = opening_feature_id(round_number, attacker, setup)
        affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
        light_trigger: WeaponAttack | None = None
        ranged_split = use_ranged_split(attacker, setup, definition.slots, dice)
        ranged_split_used = False
        turn_key = f"{round_number}:{attacker.combatant_id}"

        for index, slot in enumerate(definition.slots):
            if attacker.state.is_dead or attacker.state.is_unconscious or attacker.state.turn_terminated:
                break
            split_this_slot = (
                index > 0
                and ranged_split
                and not ranged_split_used
                and flexible_slot_has_both(attacker, slot.attack_ids)
            )
            chosen_attack = attack_choice(attacker, setup, slot, ranged_backline=split_this_slot)
            if chosen_attack is not None:
                target, attack, distance = chosen_attack
                if split_this_slot and attack.weapon.attack_kind is WeaponAttackKind.RANGED:
                    ranged_split_used = True
                pack = pack_tactics_active(attacker, target, setup)
                feature_id = opening_feature or ("pack-tactics" if pack else definition.id)
                event = resolve_encounter_attack(
                    sequence, round_number, attacker, target, attack, distance, dice, setup,
                    spend_action=False, advantage_sources=1 if pack else 0,
                    feature_id=feature_id, turn_key=turn_key, allow_reckless=True,
                    close_enemy_active=False,
                )
                events.append(event)
                sequence += 1
                if attacker.state.turn_terminated:
                    break
                cleave, sequence = resolve_cleave_extra_attack(
                    sequence, round_number, attacker, event, attack, setup, dice, turn_key,
                )
                events.extend(cleave)
                if definition.is_attack_action and light_trigger is None and attack.weapon.light:
                    light_trigger = attack
                opening_feature = None
                continue

            chosen_save = save_choice(attacker, setup, slot)
            if chosen_save is not None:
                target, save_action, distance = chosen_save
                events.append(resolve_save_action(
                    sequence, round_number, attacker, target, save_action,
                    distance, dice, spend_action=False, affected_states=affected_states,
                ))
                sequence += 1

        if definition.is_attack_action and light_trigger is not None and not attacker.state.turn_terminated:
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
