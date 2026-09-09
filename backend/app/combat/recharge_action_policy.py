from __future__ import annotations

import logging

from app.combat.pit_policy import choose_attack, save_distance, target_order
from app.combat.resources import is_recharge_resource, resource_available
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def recharge_attack_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        ids = [attack.id for attack in attacks if is_recharge_resource(attacker.state, attack.resource_id)]
        if not ids:
            return None
        return choose_attack(attacker, setup, ids)
    except Exception as exc:
        logger.exception("Failed Recharge attack choice for %s.", attacker.combatant_id)
        raise RuntimeError("Recharge attack choice could not be evaluated.") from exc


def recharge_save_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        for target in target_order(attacker, setup):
            for action in attacker.state.template.saving_throw_actions:
                if not is_recharge_resource(attacker.state, action.resource_id):
                    continue
                if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                    continue
                distance = save_distance(attacker, target, action.range_ft)
                if legal_save_action(action, target, distance):
                    return target, action, distance
        return None
    except Exception as exc:
        logger.exception("Failed Recharge save choice for %s.", attacker.combatant_id)
        raise RuntimeError("Recharge save choice could not be evaluated.") from exc


def recharge_action_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        attack = recharge_attack_choice(attacker, setup)
        save = recharge_save_choice(attacker, setup)
        if attack is not None and save is not None:
            raise ValueError(
                "Multiple legal Recharge action families require explicit source-priority metadata."
            )
        if save is not None:
            return "save", save
        if attack is not None:
            return "attack", attack
        return None
    except Exception as exc:
        logger.exception("Failed universal Recharge action priority for %s.", attacker.combatant_id)
        raise RuntimeError("Recharge action priority could not be evaluated.") from exc
