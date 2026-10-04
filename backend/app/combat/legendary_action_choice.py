from __future__ import annotations

import logging

from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.area_targeting import AreaPlacement
from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.resources import resource_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.legendary_actions import LegendaryActionOption
from app.domain.models import SavingThrowAction, WeaponAttack

logger = logging.getLogger(__name__)
RESOURCE_ID = "legendary-actions"


def attack_for(member: EncounterCombatant, attack_id: str) -> WeaponAttack | None:
    attacks = [member.state.template.weapon_attack, *member.state.template.alternate_weapon_attacks]
    return next((item for item in attacks if item.id == attack_id), None)


def attack_damage(attack: WeaponAttack) -> int:
    if attack.fixed_damage is not None:
        return attack.fixed_damage + attack.damage_bonus
    return attack.weapon.dice_count * ((attack.weapon.dice_size + 1) // 2) + attack.damage_bonus


def save_damage(action: SavingThrowAction, target_count: int) -> int:
    average = action.damage_dice_count * ((action.damage_dice_size + 1) // 2) + action.damage_bonus
    return average * target_count


def choose_legendary_attack(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[LegendaryActionOption, EncounterCombatant, WeaponAttack] | None:
    """Pick the highest-damage landable legendary attack the actor can afford."""
    try:
        if is_incapacitated(actor.state) or actor.state.is_dead or actor.state.current_hp <= 0:
            return None
        options = [
            item for item in actor.state.template.legendary_actions
            if item.kind == "attack" and resource_available(actor.state, RESOURCE_ID, item.cost)
        ]
        best: tuple[LegendaryActionOption, EncounterCombatant, WeaponAttack] | None = None
        best_damage = -1
        for option in options:
            if option.attack_id is None:
                raise ValueError(f"{actor.state.template.name} legendary action {option.id} is missing attack_id.")
            attack = attack_for(actor, option.attack_id)
            if attack is None:
                raise ValueError(
                    f"{actor.state.template.name} legendary action {option.id} "
                    f"references missing attack {option.attack_id}."
                )
            reach = attack.weapon.reach_ft
            for target in living_opponents(actor, setup):
                if combatant_distance(actor, target) > reach:
                    continue
                damage = attack_damage(attack)
                if damage > best_damage:
                    best = (option, target, attack)
                    best_damage = damage
        return best
    except Exception:
        logger.exception("Failed to choose a legendary attack for %s.", actor.combatant_id)
        raise


def choose_legendary_save(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[LegendaryActionOption, SavingThrowAction, AreaPlacement] | None:
    """Pick the highest-damage landable legendary save the actor can afford."""
    try:
        if is_incapacitated(actor.state) or actor.state.is_dead or actor.state.current_hp <= 0:
            return None
        best: tuple[LegendaryActionOption, SavingThrowAction, AreaPlacement] | None = None
        best_damage = -1
        for option in actor.state.template.legendary_actions:
            if option.kind != "save" or not resource_available(actor.state, RESOURCE_ID, option.cost):
                continue
            action = option.save_action
            if action is None or action.area is None:
                raise ValueError(f"{actor.state.template.name} legendary action {option.id} is missing a save area.")
            placements = legal_area_save_placements(actor, setup, action)
            if not placements:
                continue
            placement = placements[0]
            damage = save_damage(action, len(placement.target_ids))
            if damage > best_damage:
                best = (option, action, placement)
                best_damage = damage
        return best
    except Exception:
        logger.exception("Failed to choose a legendary save for %s.", actor.combatant_id)
        raise


def choose_legendary_action(actor: EncounterCombatant, setup: EncounterSetup):
    """Pick the landable legendary option with the most easy-to-calculate damage."""
    try:
        attack = choose_legendary_attack(actor, setup)
        save = choose_legendary_save(actor, setup)
        attack_value = attack_damage(attack[2]) if attack is not None else -1
        save_value = save_damage(save[1], len(save[2].target_ids)) if save is not None else -1
        if save_value > attack_value:
            return ("save", save)
        if attack is not None:
            return ("attack", attack)
        return None
    except Exception:
        logger.exception("Failed to choose a legendary action for %s.", actor.combatant_id)
        raise
