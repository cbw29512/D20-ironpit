"""Landing-damage Action policy for heroes and monsters."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.area_save_actions import choose_area_save
from app.combat.area_weapon_attacks import choose_area_weapon_attack
from app.combat.attack_action_choices import attack_choice
from app.combat.auto_hit_spell_policy import choose_auto_hit_spell
from app.combat.concentration_repeat_saves import choose_concentration_repeat_save
from app.combat.encounter_targeting import living_opponents
from app.combat.intimidating_presence_2014 import can_use_presence
from app.combat.multi_target_save_actions import choose_multi_target_save_action
from app.combat.pit_policy import choose_attack, save_distance, target_order
from app.combat.resources import resource_available
from app.combat.saving_throws import legal_save_action
from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.save_zone_landing import choose_damaging_save_zone
from app.combat.spell_policy import choose_spell
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OffensePick:
    family: str
    expected_damage: float
    payload: object | None = None


def weapon_mean_damage(attack: WeaponAttack) -> float:
    try:
        return attack.weapon.dice_count * (attack.weapon.dice_size + 1) / 2 + attack.damage_bonus
    except Exception:
        logger.exception("Failed printed weapon damage for %s.", attack.id)
        raise


def _save_mean_damage(action) -> float:
    try:
        parts = action.damage_components or (
            [action] if getattr(action, "damage_dice_count", 0) else []
        )
        total = 0.0
        for part in parts:
            count = getattr(part, "dice_count", getattr(part, "damage_dice_count", 0))
            size = getattr(part, "dice_size", getattr(part, "damage_dice_size", 0))
            bonus = getattr(part, "damage_bonus", 0)
            if count:
                total += count * (size + 1) / 2 + bonus
        return total
    except Exception:
        logger.exception("Failed printed save-action damage for %s.", getattr(action, "id", "?"))
        raise


def melee_can_land_now(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    try:
        ids = [
            attacker.state.template.weapon_attack.id,
            *(item.id for item in attacker.state.template.alternate_weapon_attacks),
        ]
        return choose_attack(attacker, setup, ids, kind=WeaponAttackKind.MELEE) is not None
    except Exception:
        logger.exception("Failed melee-landing probe for %s.", attacker.combatant_id)
        raise


def attack_action_melee_legal(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    try:
        definition = attacker.state.template.attack_action
        if definition is None:
            return False
        return any(
            attack_choice(attacker, setup, slot) is not None
            and choose_attack(attacker, setup, slot.attack_ids, kind=WeaponAttackKind.MELEE) is not None
            for slot in definition.slots
        )
    except Exception:
        logger.exception("Failed melee Attack-action probe for %s.", attacker.combatant_id)
        raise


def _attack_action_damage(attacker: EncounterCombatant, setup: EncounterSetup) -> float:
    definition = attacker.state.template.attack_action
    if definition is None:
        return 0.0
    total = 0.0
    for slot in definition.slots:
        chosen = attack_choice(attacker, setup, slot)
        if chosen is not None:
            total += weapon_mean_damage(chosen[1])
    return total


def _spell_offense_score(caster: EncounterCombatant, setup: EncounterSetup, turn_key: str) -> float:
    scores = []
    for choice in (
        choose_concentration_repeat_save(caster, setup),
        choose_auto_hit_spell(caster, setup, turn_key),
        choose_spell_attack(caster, setup, turn_key),
        choose_spell(caster, setup, turn_key),
    ):
        if choice is not None:
            scores.append(choice.expected_damage)
    return max(scores, default=float("-inf"))


def decide_post_move_offense(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> OffensePick:
    """Choose the landable Action family under the shared landing-damage rule."""
    try:
        if not is_available(attacker.state, "action"):
            return OffensePick("dodge", 0.0)
        melee_now = melee_can_land_now(attacker, setup)
        picks: list[OffensePick] = []
        if melee_now and attack_action_melee_legal(attacker, setup):
            picks.append(OffensePick("attack-action", _attack_action_damage(attacker, setup)))
        elif not melee_now:
            attack_action_score = _attack_action_damage(attacker, setup)
            if attacker.state.template.attack_action is not None and attack_action_score > 0:
                picks.append(OffensePick("attack-action", attack_action_score))
        ids = [
            attacker.state.template.weapon_attack.id,
            *(item.id for item in attacker.state.template.alternate_weapon_attacks),
        ]
        weapon = choose_attack(
            attacker, setup, ids,
            kind=WeaponAttackKind.MELEE if melee_now else WeaponAttackKind.RANGED,
        )
        if weapon is not None:
            picks.append(OffensePick("standard-attack", weapon_mean_damage(weapon[1]), weapon))
        if not melee_now:
            area_weapon = choose_area_weapon_attack(attacker, setup)
            if area_weapon is not None:
                picks.append(OffensePick(
                    "area-weapon",
                    weapon_mean_damage(area_weapon.attack) * len(area_weapon.placement.target_ids),
                    area_weapon,
                ))
        spell_score = _spell_offense_score(attacker, setup, turn_key)
        if spell_score != float("-inf"):
            picks.append(OffensePick("spell", max(0.0, spell_score)))
        area_save = choose_area_save(attacker, setup, action_cost="action")
        if area_save is not None:
            action, placement = area_save
            picks.append(OffensePick(
                "area-save",
                _save_mean_damage(action) * max(1, len(placement.target_ids)),
                area_save,
            ))
        multi_save = choose_multi_target_save_action(attacker, setup)
        if multi_save is not None:
            action, targets = multi_save
            picks.append(OffensePick("multi-save", _save_mean_damage(action) * len(targets), multi_save))
        chosen_save = None
        for target in target_order(attacker, setup):
            for action in attacker.state.template.saving_throw_actions:
                if action.area is not None:
                    continue
                if action.action_cost != "action" or (action.max_targets or 1) > 1:
                    continue
                if not resource_available(attacker.state, action.resource_id, action.resource_cost):
                    continue
                distance = save_distance(attacker, target, action.range_ft)
                if legal_save_action(action, target, distance):
                    chosen_save = (target, action, distance)
                    break
            if chosen_save is not None:
                break
        if chosen_save is not None:
            picks.append(OffensePick("save-action", _save_mean_damage(chosen_save[1]), chosen_save))
        save_zone = choose_damaging_save_zone(attacker, setup, turn_key)
        if save_zone is not None:
            action, center, score = save_zone
            picks.append(OffensePick("save-zone", score, (action, center)))
        damage = [item for item in picks if item.expected_damage > 0]
        if damage:
            return max(damage, key=lambda item: (
                item.expected_damage,
                1 if melee_now and item.family in {"attack-action", "standard-attack"} else 0,
                item.family,
            ))
        target = living_opponents(attacker, setup)[0] if living_opponents(attacker, setup) else None
        if target is not None and can_use_presence(attacker, target):
            return OffensePick("presence", 0.0, target)
        if picks:
            return max(picks, key=lambda item: (item.expected_damage, item.family))
        return OffensePick("dodge", 0.0)
    except Exception:
        logger.exception("Failed landing-offense decision for %s.", attacker.combatant_id)
        raise
