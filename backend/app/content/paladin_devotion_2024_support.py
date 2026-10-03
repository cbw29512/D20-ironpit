from __future__ import annotations

import logging

from app.domain.attack_action_weapon_buffs import AttackActionWeaponBuff
from app.domain.models import DamageType
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

logger = logging.getLogger(__name__)

_PROTECTED_TYPES = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"]
_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def divine_favor_2024() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="divine-favor",
            name="Divine Favor",
            level=1,
            action_cost="bonus_action",
            range_ft=0,
            duration_minutes=1,
            target_policy="self",
            concentration=False,
            priority=40,
            modifier_effects=[
                SpellModifierEffect(
                    kind="bonus-damage",
                    dice_count=1,
                    dice_size=4,
                    damage_type="radiant",
                ),
            ],
            animation="divine-favor",
            source="D&D Beyond Basic Rules 2024: Divine Favor",
        )
    except Exception:
        logger.exception("Failed to build 2024 Divine Favor.")
        raise


def protection_from_evil_and_good_2024() -> DefensiveSpellAction:
    try:
        save_advantage = [
            SpellModifierEffect(
                kind="saving-throw-advantage",
                save_ability=ability,
                source_creature_types=_PROTECTED_TYPES,
                required_effect_tags=[tag],
            )
            for tag in ("charm", "fear")
            for ability in _ABILITIES
        ]
        return DefensiveSpellAction(
            id="protection-from-evil-and-good",
            name="Protection from Evil and Good",
            level=1,
            action_cost="action",
            range_ft=5,
            duration_minutes=10,
            target_policy="friendly",
            target_count=1,
            concentration=True,
            priority=45,
            modifier_effects=[
                SpellModifierEffect(
                    kind="attacks-against-disadvantage",
                    source_creature_types=_PROTECTED_TYPES,
                ),
                SpellModifierEffect(
                    kind="condition-immunity",
                    condition_id="charmed",
                    source_creature_types=_PROTECTED_TYPES,
                ),
                SpellModifierEffect(
                    kind="condition-immunity",
                    condition_id="frightened",
                    source_creature_types=_PROTECTED_TYPES,
                ),
                *save_advantage,
            ],
            animation="protection",
            source="D&D Beyond Basic Rules 2024: Protection from Evil and Good",
        )
    except Exception:
        logger.exception("Failed to build 2024 Protection from Evil and Good.")
        raise


def shield_of_faith_2024() -> DefensiveSpellAction:
    try:
        return DefensiveSpellAction(
            id="shield-of-faith",
            name="Shield of Faith",
            level=1,
            action_cost="bonus_action",
            range_ft=60,
            duration_minutes=10,
            target_policy="friendly",
            target_count=1,
            concentration=True,
            priority=50,
            modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=2)],
            animation="shield",
            source="D&D Beyond Basic Rules 2024: Shield of Faith",
        )
    except Exception:
        logger.exception("Failed to build 2024 Shield of Faith.")
        raise


def sacred_weapon_2024(charisma_modifier: int) -> AttackActionWeaponBuff:
    try:
        return AttackActionWeaponBuff(
            id="sacred-weapon",
            name="Sacred Weapon",
            resource_id="channel-divinity",
            resource_cost=1,
            weapon_id="longsword",
            duration_rounds=100,
            attack_roll_bonus=max(1, charisma_modifier),
            damage_type_choice=DamageType.RADIANT,
            source_is_magical=True,
            animation="bless",
        )
    except Exception:
        logger.exception("Failed to build 2024 Sacred Weapon.")
        raise
