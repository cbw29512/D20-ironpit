from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attack_action_choices import attack_choice, save_choice, slot_has_legal_choice, use_ranged_split
from app.combat.attack_action_rules import validate_attack_action_slots
from app.combat.cleave import resolve_cleave_extra_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import close_ranged_threat_exists, combatant_distance
from app.combat.light_attack_resolution import resolve_light_extra_attack
from app.combat.mixed_slot_policy import prefer_save_replacement
from app.combat.opening_burst import opening_feature_id
from app.combat.pit_policy import flexible_slot_has_both
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def _apply_immediate_push(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    event: BattleEvent,
) -> None:
    push_ft = attack.push_target_away_ft
    if not event.hit or push_ft <= 0 or target.state.is_dead:
        return
    if push_ft % 5:
        raise ValueError("Immediate push distance must use 5-foot increments.")
    before = combatant_distance(attacker, target)
    source_position = attacker.state.position
    target_position = target.state.position
    if source_position is not None or target_position is not None:
        if source_position is None or target_position is None:
            raise ValueError("Immediate push cannot mix scalar and grid position authority.")
        dx = target_position.x - source_position.x
        dy = target_position.y - source_position.y
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        if step_x == step_y == 0:
            step_x = 1
        squares = push_ft // 5
        target_position.x = max(0, target_position.x + step_x * squares)
        target_position.y = max(0, target_position.y + step_y * squares)
    else:
        direction = 1 if target.position_ft >= attacker.position_ft else -1
        target.position_ft = max(0, target.position_ft + direction * push_ft)
    after = combatant_distance(attacker, target)
    event.distance_before_ft = before
    event.distance_after_ft = after
    event.description += f" Target is pushed {push_ft} ft. away ({before} ft. to {after} ft.)."


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
            chosen_save = save_choice(attacker, setup, slot)
            if chosen_save is not None and (
                chosen_attack is None
                or prefer_save_replacement(attacker, chosen_save[0], chosen_save[1])
            ):
                target, save_action, distance = chosen_save
                events.append(resolve_save_action(
                    sequence, round_number, attacker, target, save_action,
                    distance, dice, spend_action=False, affected_states=affected_states,
                ))
                sequence += 1
                continue
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
                    close_enemy_active=close_ranged_threat_exists(attacker, setup),
                )
                _apply_immediate_push(attacker, target, attack, event)
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
