from __future__ import annotations
import logging
from app.combat.action_economy import is_available
from app.combat.attack_legality import attack_allowed_against
from app.combat.offensive_range_profile import OffensiveRangeProfile
from app.combat.resources import is_recharge_resource, resource_available
from app.combat.save_action_legality import save_action_target_eligible
from app.combat.spellcasting import spell_action_resource_available
from app.domain.encounters import EncounterCombatant
from app.domain.weapons import WeaponAttackKind

logger = logging.getLogger(__name__)
OffensiveRange = tuple[str, int]
RankedOffensiveRange = tuple[int, str, int]


def _priority_for_resource(member: EncounterCombatant, resource_id: str | None) -> int:
    try:
        return 0 if is_recharge_resource(member.state, resource_id) else 1
    except Exception:
        logger.exception("Failed Recharge movement-priority probe for %s.", member.combatant_id)
        raise


def _save_action_range(action) -> int:
    try:
        if action.area is None:
            return action.range_ft
        if action.area.origin == "self":
            return action.area.length_ft or action.area.radius_ft or action.range_ft
        return action.range_ft + (action.area.radius_ft or 0)
    except Exception:
        logger.exception("Failed saving-throw action effective-range probe for %s.", action.id)
        raise


def _spell_resource_available(member: EncounterCombatant, action, turn_key: str) -> bool:
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


def _weapon_profiles(attacker: EncounterCombatant, target: EncounterCombatant) -> list[OffensiveRangeProfile]:
    try:
        profiles: list[OffensiveRangeProfile] = []
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        for attack in attacks:
            if not attack_allowed_against(attack, attacker.combatant_id, target.state):
                continue
            if not resource_available(attacker.state, attack.resource_id, attack.resource_cost):
                continue
            priority = _priority_for_resource(attacker, attack.resource_id)
            execution_rank = 0 if priority == 0 else 2
            kind = attack.weapon.attack_kind
            if kind in {WeaponAttackKind.MELEE, WeaponAttackKind.MELEE_OR_RANGED}:
                reach = attack.weapon.reach_ft
                profiles.append(OffensiveRangeProfile(priority, "melee", reach, reach, execution_rank))
            if kind in {WeaponAttackKind.RANGED, WeaponAttackKind.MELEE_OR_RANGED}:
                normal = attack.weapon.normal_range_ft
                maximum = attack.weapon.long_range_ft or normal
                if normal is not None and maximum is not None:
                    profiles.append(OffensiveRangeProfile(priority, "ranged", maximum, normal, execution_rank))
        return profiles
    except Exception:
        logger.exception("Failed weapon offensive-range probe for %s.", attacker.combatant_id)
        raise


def _save_action_profiles(attacker: EncounterCombatant, target: EncounterCombatant) -> list[OffensiveRangeProfile]:
    try:
        profiles: list[OffensiveRangeProfile] = []
        for action in attacker.state.template.saving_throw_actions:
            if action.action_cost != "action" or not is_available(attacker.state, action.action_cost):
                continue
            if not save_action_target_eligible(action, target, attacker):
                continue
            if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                continue
            distance = _save_action_range(action)
            priority = _priority_for_resource(attacker, action.resource_id)
            execution_rank = 0 if priority == 0 else 3
            profiles.append(OffensiveRangeProfile(priority, "ability", distance, distance, execution_rank))
        return profiles
    except Exception:
        logger.exception("Failed save-action offensive-range probe for %s.", attacker.combatant_id)
        raise


def _spell_profiles(attacker: EncounterCombatant, turn_key: str) -> list[OffensiveRangeProfile]:
    try:
        profiles: list[OffensiveRangeProfile] = []
        for action in attacker.state.template.spell_attack_actions:
            if action.action_cost == "reaction" or not is_available(attacker.state, action.action_cost):
                continue
            if _spell_resource_available(attacker, action, turn_key):
                profiles.append(OffensiveRangeProfile(1, "spell", action.range_ft, action.range_ft, 1))
        for action in attacker.state.template.spell_save_actions:
            if action.action_cost == "reaction" or action.concentration or not is_available(attacker.state, action.action_cost):
                continue
            if _spell_resource_available(attacker, action, turn_key):
                distance = action.range_ft + (action.area_radius_ft or 0)
                profiles.append(OffensiveRangeProfile(1, "spell", distance, distance, 1))
        for action in attacker.state.template.automatic_spell_actions:
            if action.action_cost == "reaction" or not is_available(attacker.state, action.action_cost):
                continue
            if _spell_resource_available(attacker, action, turn_key):
                profiles.append(OffensiveRangeProfile(1, "spell", action.range_ft, action.range_ft, 1))
        return profiles
    except Exception:
        logger.exception("Failed spell offensive-range probe for %s.", attacker.combatant_id)
        raise


def ranked_offensive_range_profiles_for_target(attacker: EncounterCombatant, target: EncounterCombatant, turn_key: str) -> list[OffensiveRangeProfile]:
    try:
        return [*_weapon_profiles(attacker, target), *_spell_profiles(attacker, turn_key), *_save_action_profiles(attacker, target)]
    except Exception:
        logger.exception("Failed offensive-range profile inventory for %s against %s.", attacker.combatant_id, target.combatant_id)
        raise


def ranked_offensive_ranges_for_target(attacker: EncounterCombatant, target: EncounterCombatant, turn_key: str) -> list[RankedOffensiveRange]:
    try:
        return [(profile.priority, profile.family, profile.max_range_ft) for profile in ranked_offensive_range_profiles_for_target(attacker, target, turn_key)]
    except Exception:
        logger.exception("Failed ranked offensive-range inventory for %s against %s.", attacker.combatant_id, target.combatant_id)
        raise


def offensive_ranges_for_target(attacker: EncounterCombatant, target: EncounterCombatant, turn_key: str) -> list[OffensiveRange]:
    try:
        return [(family, distance) for _, family, distance in ranked_offensive_ranges_for_target(attacker, target, turn_key)]
    except Exception:
        logger.exception("Failed offensive-range inventory for %s against %s.", attacker.combatant_id, target.combatant_id)
        raise
