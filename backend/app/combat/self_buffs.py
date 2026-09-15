from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.death_triggers import append_pending_death_triggers
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.modifier_stack import add_modifier
from app.combat.pit_policy import choose_attack
from app.combat.resources import action_resource_available, spend_action_resource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)


def _active_action(state):
    return next((a for a in state.template.self_buff_actions if a.id in state.active_buff_effect_ids), None)


def choose_ready_self_buff(state):
    return next((a for a in state.template.self_buff_actions if a.id not in state.active_buff_effect_ids and action_resource_available(state, a)), None)


def activate_self_buff(sequence: int, round_number: int, member: EncounterCombatant, action) -> BattleEvent:
    if not is_available(member.state, "action") or not action_resource_available(member.state, action):
        raise ValueError(f"{action.name} is unavailable.")
    spend(member.state, "action"); remaining = spend_action_resource(member.state, action)
    member.state.active_buff_effect_ids.append(action.id)
    expiry = round_number + action.duration_source_turns
    member.state.active_self_buff_expiry_rounds[action.id] = expiry
    if action.armor_class_bonus:
        add_modifier(member.state, CombatModifier(
            id=f"{member.combatant_id}:{action.id}:ac", source_id=member.combatant_id,
            source_effect_id=action.id, kind=ModifierKind.ARMOR_CLASS,
            flat_bonus=action.armor_class_bonus, expires_source_turn_end_round=expiry,
        ))
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        feature_id=action.id, resource_remaining=remaining,
        applied_condition_ids=[action.id], animation="feature",
        description=f"{member.state.template.name} uses {action.name} until the end of its next turn.",
    )


def save_advantage_sources(state, ability: str) -> int:
    action = _active_action(state)
    return int(action is not None and ability in action.save_advantage_abilities)


def resolve_bonus_attack(sequence, round_number, member, setup, dice, turn_key):
    action = _active_action(member.state)
    if action is None or action.bonus_action_attack_id is None or not is_available(member.state, "bonus_action"):
        return [], sequence
    choice = choose_attack(member, setup, [action.bonus_action_attack_id])
    if choice is None:
        return [], sequence
    target, attack, distance = choice
    spend(member.state, "bonus_action")
    event = resolve_encounter_attack(
        sequence, round_number, member, target, attack, distance, dice, setup,
        spend_action=False, feature_id=action.id, turn_key=turn_key,
    )
    events = [event]; sequence += 1
    sequence = append_pending_death_triggers(events, sequence, round_number, setup, dice)
    return events, sequence


def expire_self_buffs(state, round_number: int) -> list[str]:
    expired = [effect_id for effect_id, expiry in state.active_self_buff_expiry_rounds.items() if expiry <= round_number]
    if not expired:
        return []
    state.active_buff_effect_ids = [effect_id for effect_id in state.active_buff_effect_ids if effect_id not in expired]
    for effect_id in expired:
        state.active_self_buff_expiry_rounds.pop(effect_id, None)
    return expired


def finish_self_buff_turn(sequence, round_number, member, setup, dice, turn_key):
    events, sequence = resolve_bonus_attack(sequence, round_number, member, setup, dice, turn_key)
    expired = expire_self_buffs(member.state, round_number)
    for effect_id in expired:
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=member.combatant_id, actor_name=member.state.template.name,
            feature_id=effect_id, removed_condition_ids=[effect_id], animation="feature",
            description=f"{member.state.template.name}'s {effect_id.replace('-', ' ').title()} ends.",
        )); sequence += 1
    return events, sequence
