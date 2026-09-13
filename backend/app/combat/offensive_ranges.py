from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.attack_legality import attack_allowed_against
from app.combat.resources import resource_definition
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant
from app.domain.weapons import WeaponAttackKind
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)
OffensiveRange = tuple[str, int]


def _resource_available(member: EncounterCombatant, resource_id: str | None, cost: int = 1) -> bool:
    try:
        if resource_id is None:
            return True
        matches = [item for item in member.state.resources if item.id == resource_id]
        if len(matches) != 1:
            return False
        return matches[0].current_uses >= cost
    except Exception:
        logger.exception("Failed resource availability probe for %s.", member.combatant_id)
        raise


def _spell_level_available(member: EncounterCombatant, level: int, turn_key: str) -> bool:
    try:
        if level == 0:
            return True
        if not slot_spell_available(member.state, turn_key):
            return False
        return _resource_available(member, f"spell-slot-{level}")
    except Exception:
        logger.exception("Failed spell-level availability probe for %s.", member.combatant_id)
        raise


def _weapon_ranges(attacker: EncounterCombatant, target: EncounterCombatant, recharge_only: bool = False) -> list[OffensiveRange]:
    try:
        ranges: list[OffensiveRange] = []
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        for attack in attacks:
            if not attack_allowed_against(attack, attacker.combatant_id, target.state):
                continue
            if not _resource_available(attacker, attack.resource_id, attack.resource_cost):
                continue
            definition = resource_definition(attacker.state, attack.resource_id) if attack.resource_id else None
            recharge = definition is not None and definition.recharge is not None
            if recharge_only and not recharge:
                continue
            family = "recharge" if recharge else ("melee" if attack.weapon.attack_kind is WeaponAttackKind.MELEE else "ranged")
            if attack.weapon.attack_kind is WeaponAttackKind.MELEE:
                ranges.append((family, attack.weapon.reach_ft))
            else:
                maximum = attack.weapon.long_range_ft or attack.weapon.normal_range_ft
                if maximum is not None:
                    ranges.append((family, maximum))
        return ranges
    except Exception:
        logger.exception("Failed weapon offensive-range probe for %s.", attacker.combatant_id)
        raise


def _save_action_ranges(attacker: EncounterCombatant, target: EncounterCombatant, recharge_only: bool = False) -> list[OffensiveRange]:
    try:
        ranges: list[OffensiveRange] = []
        for action in attacker.state.template.saving_throw_actions:
            if action.target_max_size is not None and not size_at_most(target.state.template.size, action.target_max_size):
                continue
            if not _resource_available(attacker, action.resource_id, action.resource_cost):
                continue
            definition = resource_definition(attacker.state, action.resource_id) if action.resource_id else None
            if recharge_only and (definition is None or definition.recharge is None):
                continue
            ranges.append(("recharge" if definition and definition.recharge else "ability", action.range_ft))
        return ranges
    except Exception:
        logger.exception("Failed save-action offensive-range probe for %s.", attacker.combatant_id)
        raise


def _spell_ranges(attacker: EncounterCombatant, turn_key: str) -> list[OffensiveRange]:
    try:
        ranges: list[OffensiveRange] = []
        for action in attacker.state.template.spell_attack_actions:
            if action.action_cost == "reaction" or not is_available(attacker.state, action.action_cost):
                continue
            if _spell_level_available(attacker, action.level, turn_key):
                ranges.append(("spell", action.range_ft))
        for action in attacker.state.template.spell_save_actions:
            if action.action_cost == "reaction" or action.concentration or not is_available(attacker.state, action.action_cost):
                continue
            if not _spell_level_available(attacker, action.level, turn_key):
                continue
            maximum = action.range_ft + (action.area_radius_ft or 0)
            ranges.append(("spell", maximum))
        return ranges
    except Exception:
        logger.exception("Failed spell offensive-range probe for %s.", attacker.combatant_id)
        raise


def offensive_ranges_for_target(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    turn_key: str,
) -> list[OffensiveRange]:
    try:
        recharge_ranges = [*_weapon_ranges(attacker, target, True), *_save_action_ranges(attacker, target, True)]
        if recharge_ranges:
            return recharge_ranges
        return [
            *_weapon_ranges(attacker, target),
            *_spell_ranges(attacker, turn_key),
            *_save_action_ranges(attacker, target),
        ]
    except Exception:
        logger.exception(
            "Failed offensive-range inventory for %s against %s.",
            attacker.combatant_id,
            target.combatant_id,
        )
        raise
