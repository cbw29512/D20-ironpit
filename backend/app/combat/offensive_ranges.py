from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.attack_legality import attack_allowed_against
from app.combat.spell_policy import spell_has_higher_slot_scaling
from app.combat.spellcasting import legal_slot_levels, slot_spell_available
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


def _weapon_ranges(attacker: EncounterCombatant, target: EncounterCombatant) -> list[OffensiveRange]:
    try:
        ranges: list[OffensiveRange] = []
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        for attack in attacks:
            if not attack_allowed_against(attack, attacker.combatant_id, target.state):
                continue
            if attack.weapon.attack_kind is WeaponAttackKind.MELEE:
                ranges.append(("melee", attack.weapon.reach_ft))
            else:
                maximum = attack.weapon.long_range_ft or attack.weapon.normal_range_ft
                if maximum is not None:
                    ranges.append(("ranged", maximum))
        return ranges
    except Exception:
        logger.exception("Failed weapon offensive-range probe for %s.", attacker.combatant_id)
        raise


def _save_action_ranges(attacker: EncounterCombatant, target: EncounterCombatant) -> list[OffensiveRange]:
    try:
        ranges: list[OffensiveRange] = []
        for action in attacker.state.template.saving_throw_actions:
            if action.target_max_size is not None and not size_at_most(target.state.template.size, action.target_max_size):
                continue
            if not _resource_available(attacker, action.resource_id, action.resource_cost):
                continue
            ranges.append(("ability", action.range_ft))
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
        for action in attacker.state.template.auto_hit_spell_actions:
            if action.action_cost == "reaction" or not is_available(attacker.state, action.action_cost):
                continue
            if legal_slot_levels(
                attacker.state, turn_key, action.level,
                higher_slot_scaling=action.projectiles_per_slot_above > 0,
            ):
                ranges.append(("spell", action.range_ft))
        for action in attacker.state.template.spell_save_actions:
            if action.action_cost == "reaction" or action.concentration or not is_available(attacker.state, action.action_cost):
                continue
            if not legal_slot_levels(
                attacker.state, turn_key, action.level,
                higher_slot_scaling=spell_has_higher_slot_scaling(action),
            ):
                continue
            maximum = action.range_ft + (action.area_radius_ft or 0)
            ranges.append(("spell", maximum))
        return ranges
    except Exception:
        logger.exception("Failed spell offensive-range probe for %s.", attacker.combatant_id)
        raise


def tightest_usable_melee_reach_ft(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
) -> int | None:
    """Smallest currently legal melee reach among Attack/Multiattack slots, else any melee."""
    try:
        attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        by_id = {attack.id: attack for attack in attacks}
        reaches: list[int] = []
        definition = attacker.state.template.attack_action
        if definition is not None:
            for slot in definition.slots:
                for attack_id in slot.attack_ids:
                    attack = by_id.get(attack_id)
                    if (
                        attack is not None
                        and attack.weapon.attack_kind is WeaponAttackKind.MELEE
                        and attack_allowed_against(attack, attacker.combatant_id, target.state)
                    ):
                        reaches.append(attack.weapon.reach_ft)
        if not reaches:
            for attack in attacks:
                if (
                    attack.weapon.attack_kind is WeaponAttackKind.MELEE
                    and attack_allowed_against(attack, attacker.combatant_id, target.state)
                ):
                    reaches.append(attack.weapon.reach_ft)
        return min(reaches) if reaches else None
    except Exception:
        logger.exception(
            "Failed tightest melee-reach probe for %s against %s.",
            attacker.combatant_id,
            target.combatant_id,
        )
        raise


def offensive_ranges_for_target(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    turn_key: str,
) -> list[OffensiveRange]:
    try:
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
