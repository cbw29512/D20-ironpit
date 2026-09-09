from __future__ import annotations

import logging

from app.combat.area_targeting import legal_area_placements
from app.combat.offense_value import save_action_expected_damage
from app.combat.pit_policy import choose_attack, save_distance, target_order
from app.combat.resources import is_recharge_resource, resource_available
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def recharge_attack_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        ids = [attack.id for attack in attacks if is_recharge_resource(attacker.state, attack.resource_id)]
        return choose_attack(attacker, setup, ids) if ids else None
    except Exception as exc:
        logger.exception("Failed Recharge attack choice for %s.", attacker.combatant_id)
        raise RuntimeError("Recharge attack choice could not be evaluated.") from exc


def recharge_save_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        for target in target_order(attacker, setup):
            for action in attacker.state.template.saving_throw_actions:
                if action.area is not None or not is_recharge_resource(attacker.state, action.resource_id):
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


def recharge_area_save_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        candidates = []
        for index, action in enumerate(attacker.state.template.saving_throw_actions):
            if action.area is None or not is_recharge_resource(attacker.state, action.resource_id):
                continue
            if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                continue
            placements = legal_area_placements(attacker, setup, action.area, action.range_ft)
            for placement in placements:
                score = sum(save_action_expected_damage(members[target_id], action) for target_id in placement.target_ids)
                candidates.append((score, len(placement.target_ids), -index, action, placement))
        if not candidates:
            return None
        _, _, _, action, placement = max(candidates, key=lambda row: row[:3])
        return action, placement
    except Exception as exc:
        logger.exception("Failed Recharge area-save choice for %s.", attacker.combatant_id)
        raise RuntimeError("Recharge area-save choice could not be evaluated.") from exc


def recharge_action_choice(attacker: EncounterCombatant, setup: EncounterSetup):
    try:
        choices = [
            ("attack", recharge_attack_choice(attacker, setup)),
            ("save", recharge_save_choice(attacker, setup)),
            ("area-save", recharge_area_save_choice(attacker, setup)),
        ]
        legal = [(kind, payload) for kind, payload in choices if payload is not None]
        if len(legal) > 1:
            raise ValueError("Multiple legal Recharge action families require explicit source-priority metadata.")
        return legal[0] if legal else None
    except Exception as exc:
        logger.exception("Failed universal Recharge action priority for %s.", attacker.combatant_id)
        raise RuntimeError("Recharge action priority could not be evaluated.") from exc
