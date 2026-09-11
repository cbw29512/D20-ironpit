from __future__ import annotations
import logging
from app.combat.action_economy import is_available
from app.combat.attack_legality import attack_allowed_against
from app.combat.resources import is_recharge_resource, resource_available
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant
from app.domain.weapons import WeaponAttackKind
from app.domain.size import size_at_most

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


def _spell_level_available(member: EncounterCombatant, level: int, turn_key: str) -> bool:
    try:
        if level == 0:
            return True
        if not slot_spell_available(member.state, turn_key):
            return False
        return resource_available(member.state, f"spell-slot-{level}")
    except Exception:
        logger.exception("Failed spell-level availability probe for %s.", member.combatant_id)
        raise


def _ranked_weapon_ranges(attacker: EncounterCombatant, target: EncounterCombatant) -> list[RankedOffensiveRange]:
    try:
        ranges: list[RankedOffensiveRange] = []
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        for attack in attacks:
            if not attack_allowed_against(attack, attacker.combatant_id, target.state):
                continue
            if not resource_available(attacker.state, attack.resource_id, attack.resource_cost):
                continue
            priority = _priority_for_resource(attacker, attack.resource_id)
            kind = attack.weapon.attack_kind
            if kind in {WeaponAttackKind.MELEE, WeaponAttackKind.MELEE_OR_RANGED}:
                ranges.append((priority, "melee", attack.weapon.reach_ft))
            if kind in {WeaponAttackKind.RANGED, WeaponAttackKind.MELEE_OR_RANGED}:
                maximum = attack.weapon.long_range_ft or attack.weapon.normal_range_ft
                if maximum is not None:
                    ranges.append((priority, "ranged", maximum))
        return ranges
    except Exception:
        logger.exception("Failed weapon offensive-range probe for %s.", attacker.combatant_id)
        raise


def _ranked_save_action_ranges(attacker: EncounterCombatant, target: EncounterCombatant) -> list[RankedOffensiveRange]:
    try:
        ranges: list[RankedOffensiveRange] = []
        for action in attacker.state.template.saving_throw_actions:
            if action.target_max_size is not None and not size_at_most(target.state.template.size, action.target_max_size):
                continue
            if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                continue
            ranges.append((_priority_for_resource(attacker, action.resource_id), "ability", _save_action_range(action)))
        return ranges
    except Exception:
        logger.exception("Failed save-action offensive-range probe for %s.", attacker.combatant_id)
        raise


def _ranked_spell_ranges(attacker: EncounterCombatant, turn_key: str) -> list[RankedOffensiveRange]:
    try:
        ranges: list[RankedOffensiveRange] = []
        for action in attacker.state.template.spell_attack_actions:
            if action.action_cost == "reaction" or not is_available(attacker.state, action.action_cost):
                continue
            if _spell_level_available(attacker, action.level, turn_key):
                ranges.append((1, "spell", action.range_ft))
        for action in attacker.state.template.spell_save_actions:
            if action.action_cost == "reaction" or action.concentration or not is_available(attacker.state, action.action_cost):
                continue
            if _spell_level_available(attacker, action.level, turn_key):
                ranges.append((1, "spell", action.range_ft + (action.area_radius_ft or 0)))
        return ranges
    except Exception:
        logger.exception("Failed spell offensive-range probe for %s.", attacker.combatant_id)
        raise


def ranked_offensive_ranges_for_target(attacker: EncounterCombatant, target: EncounterCombatant, turn_key: str) -> list[RankedOffensiveRange]:
    try:
        return [*_ranked_weapon_ranges(attacker, target), *_ranked_spell_ranges(attacker, turn_key), *_ranked_save_action_ranges(attacker, target)]
    except Exception:
        logger.exception("Failed ranked offensive-range inventory for %s against %s.", attacker.combatant_id, target.combatant_id)
        raise


def offensive_ranges_for_target(attacker: EncounterCombatant, target: EncounterCombatant, turn_key: str) -> list[OffensiveRange]:
    try:
        return [(family, distance) for _, family, distance in ranked_offensive_ranges_for_target(attacker, target, turn_key)]
    except Exception:
        logger.exception("Failed offensive-range inventory for %s against %s.", attacker.combatant_id, target.combatant_id)
        raise