from __future__ import annotations

from app.combat.attack_legality import attack_allowed_against
from app.combat.encounter_targeting import combatant_distance
from app.combat.policy import preferred_distance_for_attacks, select_allowed_weapon_attack
from app.combat.saving_throws import legal_save_action
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant


def validate_attack_action_slots(attacker: EncounterCombatant) -> None:
    definition = attacker.state.template.attack_action
    if definition is None:
        raise ValueError("Combatant has no Multiattack action.")
    attacks = {
        attacker.state.template.weapon_attack.id,
        *(attack.id for attack in attacker.state.template.alternate_weapon_attacks),
    }
    saves = {action.id for action in attacker.state.template.saving_throw_actions}
    for slot in definition.slots:
        unknown = (set(slot.attack_ids) - attacks) | (set(slot.save_action_ids) - saves)
        if unknown:
            raise ValueError(f"Unknown Multiattack IDs in {definition.name}: {sorted(unknown)}")


def attack_action_slot_choice(attacker, target, slot):
    distance = combatant_distance(attacker, target)
    profiles = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
    legal_ids = [
        attack.id for attack in profiles
        if attack.id in slot.attack_ids
        and attack_allowed_against(attack, attacker.combatant_id, target.state)
    ]
    attack = select_allowed_weapon_attack(attacker.state, distance, legal_ids)
    allowed = set(slot.save_action_ids)
    save = None if attack is not None else next((
        action for action in attacker.state.template.saving_throw_actions
        if action.id in allowed and legal_save_action(action, target, distance)
    ), None)
    return attack, save


def preferred_attack_action_distance(
    attacker: EncounterCombatant,
    slot: AttackActionSlot,
) -> int:
    if slot.attack_ids:
        return preferred_distance_for_attacks(attacker.state, slot.attack_ids)
    allowed = set(slot.save_action_ids)
    ranges = [
        action.range_ft for action in attacker.state.template.saving_throw_actions
        if action.id in allowed
    ]
    if not ranges:
        raise ValueError("Multiattack slot has no known action range.")
    return max(ranges)
