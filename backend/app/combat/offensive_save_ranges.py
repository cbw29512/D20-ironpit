from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.offense_value import save_action_expected_damage
from app.combat.offensive_range_profile import OffensiveRangeProfile
from app.combat.resources import is_recharge_resource, resource_available
from app.combat.save_action_legality import save_action_target_eligible
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def effective_action_range(action) -> int:
    try:
        if action.area is None:
            return action.range_ft
        area_reach = action.area.length_ft or action.area.radius_ft or 0
        return area_reach if action.area.origin == "self" else action.range_ft + area_reach
    except Exception:
        logger.exception("Failed action effective-range probe for %s.", action.id)
        raise


def _priority_for_resource(member: EncounterCombatant, resource_id: str | None) -> int:
    try:
        return 0 if is_recharge_resource(member.state, resource_id) else 1
    except Exception:
        logger.exception("Failed Recharge movement-priority probe for %s.", member.combatant_id)
        raise


def _attack_action_save_ids(attacker: EncounterCombatant) -> set[str]:
    definition = attacker.state.template.attack_action
    if definition is None:
        return set()
    return {save_id for slot in definition.slots for save_id in slot.save_action_ids}


def save_action_profiles(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
) -> list[OffensiveRangeProfile]:
    try:
        profiles: list[OffensiveRangeProfile] = []
        attack_action_save_ids = _attack_action_save_ids(attacker)
        for action in attacker.state.template.saving_throw_actions:
            if action.action_cost != "action" or not is_available(attacker.state, action.action_cost):
                continue
            if not save_action_target_eligible(action, target, attacker):
                continue
            if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                continue
            distance = effective_action_range(action)
            priority = _priority_for_resource(attacker, action.resource_id)
            execution_rank = 0 if priority == 0 else (2 if action.id in attack_action_save_ids else 3)
            value = save_action_expected_damage(target, action)
            profiles.append(
                OffensiveRangeProfile(priority, "ability", distance, distance, execution_rank, value)
            )
        return profiles
    except Exception:
        logger.exception("Failed save-action offensive-range probe for %s.", attacker.combatant_id)
        raise
