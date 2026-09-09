from __future__ import annotations

import logging

from app.combat.encounter_turn_support import save_choice
from app.combat.pit_policy import choose_attack
from app.combat.resources import is_recharge_resource
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
        recharge_ids = {
            action.id
            for action in attacker.state.template.saving_throw_actions
            if is_recharge_resource(attacker.state, action.resource_id)
        }
        if not recharge_ids:
            return None
        choice = save_choice(attacker, setup)
        if choice is not None and choice[1].id in recharge_ids:
            return choice
        for action in attacker.state.template.saving_throw_actions:
            if action.id not in recharge_ids:
                continue
            original = attacker.state.template.saving_throw_actions
            try:
                attacker.state.template.saving_throw_actions = [action]
                choice = save_choice(attacker, setup)
            finally:
                attacker.state.template.saving_throw_actions = original
            if choice is not None:
                return choice
        return None
    except Exception as exc:
        logger.exception("Failed Recharge save choice for %s.", attacker.combatant_id)
        raise RuntimeError("Recharge save choice could not be evaluated.") from exc
