from __future__ import annotations

import logging

from app.combat.attack_legality import attack_allowed_against
from app.combat.offensive_range_profile import OffensiveRangeProfile
from app.combat.resources import is_recharge_resource, resource_available
from app.combat.weapon_offense_value import weapon_attack_expected_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons import WeaponAttackKind

logger = logging.getLogger(__name__)


def _priority_for_resource(member: EncounterCombatant, resource_id: str | None) -> int:
    try:
        return 0 if is_recharge_resource(member.state, resource_id) else 1
    except Exception:
        logger.exception("Failed Recharge movement-priority probe for %s.", member.combatant_id)
        raise


def _attack_action_ids(attacker: EncounterCombatant) -> set[str]:
    definition = attacker.state.template.attack_action
    if definition is None:
        return set()
    return {attack_id for slot in definition.slots for attack_id in slot.attack_ids}


def weapon_profiles(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup | None = None,
) -> list[OffensiveRangeProfile]:
    try:
        profiles: list[OffensiveRangeProfile] = []
        attack_action_ids = _attack_action_ids(attacker)
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        for attack in attacks:
            if not attack_allowed_against(attack, attacker.combatant_id, target.state):
                continue
            if not resource_available(attacker.state, attack.resource_id, attack.resource_cost):
                continue
            priority = _priority_for_resource(attacker, attack.resource_id)
            execution_rank = 0 if priority == 0 else (2 if attack.id in attack_action_ids else 4)
            kind = attack.weapon.attack_kind
            if kind in {WeaponAttackKind.MELEE, WeaponAttackKind.MELEE_OR_RANGED}:
                reach = attack.weapon.reach_ft
                value = weapon_attack_expected_damage(attacker, target, attack, setup, reach) if setup else 0.0
                profiles.append(OffensiveRangeProfile(priority, "melee", reach, reach, execution_rank, value))
            if kind in {WeaponAttackKind.RANGED, WeaponAttackKind.MELEE_OR_RANGED}:
                normal = attack.weapon.normal_range_ft
                maximum = attack.weapon.long_range_ft or normal
                if normal is None or maximum is None:
                    continue
                value = weapon_attack_expected_damage(attacker, target, attack, setup, normal) if setup else 0.0
                profiles.append(OffensiveRangeProfile(priority, "ranged", maximum, normal, execution_rank, value))
        return profiles
    except Exception:
        logger.exception("Failed weapon offensive-range probe for %s.", attacker.combatant_id)
        raise
