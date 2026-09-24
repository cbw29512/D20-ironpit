from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.level_resources import cleric_2014_channel_divinity_uses, cleric_2014_divine_intervention_uses
from app.content.spell_slot_progression import spell_slot_resources
from app.domain.character_builds import AbilityScores
from app.domain.healing_riders import OutgoingHealingDiceMaximizer
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.models import DamageType, ResourceDefinition, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant, SlotHealingSelfRider

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def build_seraphine_weapon_attack(
    weapon: Weapon,
    scores: AbilityScores,
    level: int,
) -> WeaponAttack:
    try:
        ability = "dexterity" if weapon.attack_kind is WeaponAttackKind.RANGED else "strength"
        modifier = scores.modifier(ability)
        return WeaponAttack(
            id=f"seraphine-2014-{weapon.id}",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + modifier,
            damage_bonus=modifier,
            attack_ability=ability,
            attack_ability_modifier=modifier,
        )
    except Exception:
        logger.exception("Failed to compile Seraphine's 2014 %s attack.", weapon.id)
        raise


def seraphine_warhammer() -> Weapon:
    try:
        return Weapon(
            id="warhammer",
            name="Warhammer",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.BLUDGEONING,
            animation="blunt-strike",
            reach_ft=5,
            mastery_property=None,
            versatile=True,
        )
    except Exception:
        logger.exception("Failed to build Seraphine's 2014 Warhammer.")
        raise


def seraphine_light_crossbow() -> Weapon:
    try:
        return Weapon(
            id="light-crossbow",
            name="Light Crossbow",
            attack_kind=WeaponAttackKind.RANGED,
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.PIERCING,
            animation="projectile",
            normal_range_ft=80,
            long_range_ft=320,
            projectile="bolt",
            mastery_property=None,
            two_handed=True,
        )
    except Exception:
        logger.exception("Failed to build Seraphine's 2014 Light Crossbow.")
        raise


def build_cleric_resources_2014(level: int) -> list[ResourceDefinition]:
    try:
        resources = [
            ResourceDefinition(
                id=resource_id,
                name=f"Level {resource_id.split('-')[-1]} Spell Slot",
                max_uses=uses,
            )
            for resource_id, uses in spell_slot_resources("cleric", level).items()
        ]
        channel_uses = cleric_2014_channel_divinity_uses(level)
        if channel_uses:
            resources.append(
                ResourceDefinition(
                    id="channel-divinity",
                    name="Channel Divinity",
                    max_uses=channel_uses,
                )
            )
        intervention_uses = cleric_2014_divine_intervention_uses(level)
        if intervention_uses:
            resources.append(
                ResourceDefinition(
                    id="divine-intervention",
                    name="Divine Intervention",
                    max_uses=intervention_uses,
                )
            )
        return resources
    except Exception:
        logger.exception("Failed to build 2014 Cleric resources at level %s.", level)
        raise


def build_cleric_progression_2014(level: int) -> ProgressionCombatFeatures:
    try:
        return ProgressionCombatFeatures(
            turning_failure_destroy_max_cr=("4" if level >= 17 else "3" if level >= 14 else "2" if level >= 11 else "1" if level >= 8 else "1/2" if level >= 5 else None),
            slot_healing_other_self_rider=(
                SlotHealingSelfRider(
                    source_id="blessed-healer",
                    flat_bonus=2,
                    per_slot_level=1,
                )
                if level >= 6 else None
            ),
            outgoing_healing_dice_maximizer=(
                OutgoingHealingDiceMaximizer(
                    source_id="supreme-healing",
                    source_name="Supreme Healing",
                )
                if level >= 17 else None
            ),
            once_per_turn_weapon_hit_damage_rider=(
                OncePerTurnWeaponHitDamageRider(
                    source_id="divine-strike",
                    source_name="Divine Strike",
                    dice_count=(2 if level >= 14 else 1),
                    dice_size=8,
                    damage_type="radiant",
                )
                if level >= 8 else None
            ),
            saving_throw_advantage_grants=[
                SavingThrowAdvantageGrant(
                    source_id="dwarven-resilience",
                    source_name="Dwarven Resilience",
                    abilities=_ABILITIES,
                    against_effect_tags=["poison", "poisoned"],
                )
            ],
        )
    except Exception:
        logger.exception("Failed to build 2014 Cleric progression features at level %s.", level)
        raise
