from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.level_resources import cleric_2014_channel_divinity_uses, cleric_2014_divine_intervention_uses
from app.content.spell_slot_progression import spell_slot_resources
from app.domain.character_builds import AbilityScores
from app.domain.models import DamageType, ResourceDefinition, Weapon, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)

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
