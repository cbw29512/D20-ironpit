from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.offense_value import automatic_spell_expected_damage, save_action_expected_damage, spell_attack_expected_damage
from app.combat.offensive_range_profile import OffensiveRangeProfile
from app.combat.offensive_save_ranges import effective_action_range
from app.combat.spellcasting import spell_action_resource_available
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _resource_available(member: EncounterCombatant, action, turn_key: str) -> bool:
    try:
        return spell_action_resource_available(
            member.state,
            level=action.level,
            resource_id=action.resource_id,
            resource_cost=action.resource_cost,
            turn_key=turn_key,
        )
    except Exception:
        logger.exception("Failed spell resource probe for %s.", member.combatant_id)
        raise


def spell_profiles(
    attacker: EncounterCombatant,
    turn_key: str,
    target: EncounterCombatant | None = None,
    setup: EncounterSetup | None = None,
) -> list[OffensiveRangeProfile]:
    try:
        profiles: list[OffensiveRangeProfile] = []
        for action in attacker.state.template.spell_attack_actions:
            if action.action_cost == "reaction" or not is_available(attacker.state, action.action_cost):
                continue
            if not _resource_available(attacker, action, turn_key):
                continue
            value = spell_attack_expected_damage(attacker, target, action, setup) if target and setup else 0.0
            profiles.append(OffensiveRangeProfile(1, "spell", action.range_ft, action.range_ft, 1, value))
        for action in attacker.state.template.spell_save_actions:
            if action.action_cost == "reaction" or action.concentration or not is_available(attacker.state, action.action_cost):
                continue
            if not _resource_available(attacker, action, turn_key):
                continue
            distance = effective_action_range(action)
            value = save_action_expected_damage(target, action) if target else 0.0
            profiles.append(OffensiveRangeProfile(1, "spell", distance, distance, 1, value))
        for action in attacker.state.template.automatic_spell_actions:
            if action.action_cost == "reaction" or not is_available(attacker.state, action.action_cost):
                continue
            if not _resource_available(attacker, action, turn_key):
                continue
            value = automatic_spell_expected_damage(target, action) if target else 0.0
            profiles.append(OffensiveRangeProfile(1, "spell", action.range_ft, action.range_ft, 1, value))
        return profiles
    except Exception:
        logger.exception("Failed spell offensive-range probe for %s.", attacker.combatant_id)
        raise
