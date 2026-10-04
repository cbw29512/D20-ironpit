from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.attack_bonus_rules import compile_weapon_attack_bonus
from app.content.cleric_life_domain import AID, DISPEL_MAGIC, LESSER_RESTORATION
from app.content.druid_2024_spells import build_barkskin_2024, build_longstrider_2024
from app.content.healing_spell_effects import build_cure_wounds
from app.content.ranger_hunter_2024_spells import ensnaring_strike_2024, hunters_mark_2024
from app.content.shared_movement_spells_2024 import freedom_of_movement_2024
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot, HealingAction
from app.domain.models import WeaponAttack
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)
_MASTERED = frozenset({"longbow", "shortsword"})


def build_rowan_2024_attack(weapon_id: str, dexterity: int, level: int) -> WeaponAttack:
    try:
        weapon = build_weapon(weapon_id)
        if weapon_id not in _MASTERED:
            weapon = weapon.model_copy(update={"mastery_property": None})
        styles = ["Archery"] if level >= 2 else []
        return WeaponAttack(
            id=f"rowan-2024-{weapon_id}",
            weapon=weapon,
            attack_bonus=compile_weapon_attack_bonus(
                proficiency_bonus(level) + dexterity, styles, weapon.attack_kind,
            ),
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build 2024 Rowan attack %s at level %s.", weapon_id, level)
        raise


def build_rowan_2024_attack_action(level: int) -> AttackActionDefinition | None:
    try:
        if level < 5:
            return None
        choices = ["rowan-2024-longbow", "rowan-2024-shortsword", "rowan-2024-scimitar"]
        return AttackActionDefinition(
            id="extra-attack",
            name="Extra Attack",
            slots=[AttackActionSlot(attack_ids=choices), AttackActionSlot(attack_ids=choices)],
            is_attack_action=True,
        )
    except Exception:
        logger.exception("Failed to build 2024 Rowan Extra Attack at level %s.", level)
        raise


def ranger_2024_skill_bonuses(scores, level: int) -> dict[str, int]:
    try:
        pb = proficiency_bonus(level)
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        perception = pb * (2 if level >= 2 else 1)
        expertise = pb * (2 if level >= 9 else 1)
        return {
            "athletics": scores.modifier("strength") + pb,
            "survival": wisdom + expertise,
            "perception": wisdom + perception,
            "stealth": dexterity + expertise,
            "insight": wisdom + pb,
            "investigation": scores.modifier("intelligence") + pb,
        }
    except Exception:
        logger.exception("Failed to compile 2024 Rowan skills at level %s.", level)
        raise


def build_rowan_2024_marks(level: int, save_dc: int):
    try:
        return (
            [hunters_mark_2024(dice_size=10 if level >= 20 else 6)],
            [ensnaring_strike_2024(save_dc)],
        )
    except Exception:
        logger.exception("Failed to bind 2024 Rowan mark spells at level %s.", level)
        raise


def build_rowan_2024_spell_actions(level: int, wisdom: int):
    try:
        defensive = [build_longstrider_2024()] if level >= 2 else []
        if level >= 5:
            defensive.extend([AID.model_copy(deep=True), build_barkskin_2024()])
        if level >= 13:
            defensive.append(freedom_of_movement_2024())
        healing = [build_cure_wounds(max(0, wisdom))]
        if level >= 10:
            healing.append(HealingAction(
                id="tireless", name="Tireless", action_cost="action", range_ft=0,
                target_mode="self", dice_count=1, dice_size=8,
                healing_bonus=max(0, wisdom), resource_id="tireless",
                grants_temporary_hp=True, animation="tireless",
            ))
        removal = [LESSER_RESTORATION.model_copy(deep=True)] if level >= 5 else []
        dispel = [DISPEL_MAGIC.model_copy(deep=True)] if level >= 9 else []
        return defensive, healing, removal, dispel
    except Exception:
        logger.exception("Failed to bind 2024 Rowan spell actions at level %s.", level)
        raise


def natures_veil_2024(level: int) -> list[TimedSelfBuffAction]:
    try:
        if level < 14:
            return []
        return [TimedSelfBuffAction(
            id="natures-veil",
            name="Nature's Veil",
            action_cost="bonus_action",
            resource_id="natures-veil",
            duration_rounds=2,
            condition_ids=["invisible"],
            expiry_timing="source_turn_end",
            animation="natures-veil",
        )]
    except Exception:
        logger.exception("Failed to compile Nature's Veil at level %s.", level)
        raise
