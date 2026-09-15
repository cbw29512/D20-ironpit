from __future__ import annotations

from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.range import resolve_attack_roll_mode
from app.combat.resources import resource_available
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.legendary_actions import LegendaryActionOption

LEGENDARY_ACTION_RESOURCE_ID = "legendary-actions"


def attack_target(owner: EncounterCombatant, setup: EncounterSetup, option: LegendaryActionOption):
    if option.attack_id is None:
        return None
    attacks = [owner.state.template.weapon_attack, *owner.state.template.alternate_weapon_attacks]
    attack = next((item for item in attacks if item.id == option.attack_id), None)
    if attack is None:
        return None
    candidates = []
    for target in living_opponents(owner, setup):
        distance = combatant_distance(owner, target)
        try:
            resolve_attack_roll_mode(attack.weapon, distance, close_enemy_active=False)
        except ValueError:
            continue
        candidates.append((distance, target.combatant_id, target))
    if not candidates:
        return None
    distance, _, target = min(candidates, key=lambda item: (item[0], item[1]))
    return target, attack, distance


def single_save_target(owner: EncounterCombatant, setup: EncounterSetup, option: LegendaryActionOption):
    action = option.save_action
    if action is None or action.area is not None:
        return None
    candidates = []
    for target in living_opponents(owner, setup):
        distance = combatant_distance(owner, target)
        if legal_save_action(action, target, distance):
            candidates.append((distance, target.combatant_id, target))
    if not candidates:
        return None
    distance, _, target = min(candidates, key=lambda item: (item[0], item[1]))
    return target, distance


def option_priority(owner: EncounterCombatant, setup: EncounterSetup, option: LegendaryActionOption):
    if not resource_available(owner.state, LEGENDARY_ACTION_RESOURCE_ID, option.cost):
        return None
    if option.kind == "save" and option.save_action is not None and option.save_action.area is not None:
        placements = legal_area_save_placements(owner, setup, option.save_action)
        if not placements:
            return None
        target_count = len(placements[0].target_ids)
        return (0 if target_count > 1 else 2, -target_count, option.id)
    if option.kind == "attack":
        return (1, 0, option.id) if attack_target(owner, setup, option) is not None else None
    if option.kind == "save":
        return (2, 0, option.id) if single_save_target(owner, setup, option) is not None else None
    if option.kind == "ability_check":
        return (3, 0, option.id)
    return None
