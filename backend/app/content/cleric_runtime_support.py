from __future__ import annotations

import logging

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.domain.models import (
    DamageType,
    ResourceDefinition,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)

logger = logging.getLogger(__name__)


def ability_modifier(score: int) -> int:
    try:
        return (score - 10) // 2
    except Exception:
        logger.exception("Failed Cleric ability modifier calculation for score %s.", score)
        raise


def cleric_features(level: int) -> tuple[str, ...]:
    try:
        return canonical_combat_features("cleric", level, "life-domain")
    except Exception:
        logger.exception("Failed to compile Cleric combat features at level %s.", level)
        raise


def build_mace_attack(attack_bonus: int) -> WeaponAttack:
    try:
        return WeaponAttack(
            id="seraphine-mace",
            weapon=Weapon(
                id="mace",
                name="Mace",
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=1,
                dice_size=6,
                damage_type=DamageType.BLUDGEONING,
                animation="blunt-strike",
                reach_ft=5,
            ),
            attack_bonus=attack_bonus,
            damage_bonus=0,
        )
    except Exception:
        logger.exception("Failed to build Seraphine mace attack at bonus %s.", attack_bonus)
        raise


def build_cleric_resources(level: int) -> list[ResourceDefinition]:
    try:
        row = CLERIC_COMBAT_LEVELS[level]
        resources = [
            ResourceDefinition(
                id=f"spell-slot-{spell_level}",
                name=f"Level {spell_level} Spell Slot",
                max_uses=uses,
            )
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        if row.channel_divinity_uses:
            resources.append(ResourceDefinition(
                id="channel-divinity",
                name="Channel Divinity",
                max_uses=row.channel_divinity_uses,
            ))
        if level >= 10:
            resources.append(ResourceDefinition(
                id="divine-intervention",
                name="Divine Intervention",
                max_uses=1,
            ))
        resources.extend((
            ResourceDefinition(
                id="adrenaline-rush",
                name="Adrenaline Rush",
                max_uses=row.proficiency_bonus,
            ),
            ResourceDefinition(
                id="relentless-endurance",
                name="Relentless Endurance",
                max_uses=1,
            ),
        ))
        return resources
    except Exception:
        logger.exception("Failed to build Cleric resources at level %s.", level)
        raise


def cleric_source(level: int) -> str:
    try:
        parts = [
            f"D&D Beyond Basic Rules 2024: Cleric level {level}, Orc, Sage, Protector",
            "Sacred Flame, Bless, Cure Wounds, Guiding Bolt, Shield of Faith",
        ]
        if level >= 2:
            parts.append("Healing Word, Channel Divinity")
        if level >= 3:
            parts.append("Life Domain, Aid, Lesser Restoration, Disciple of Life")
        if level >= 4:
            parts.append("Ability Score Improvement, Mending, Inflict Wounds")
        if level >= 5:
            parts.append("Sear Undead, Mass Healing Word, Revivify, Dispel Magic")
        if level >= 6:
            parts.append("Blessed Healer")
        if level >= 7:
            parts.append("Blessed Strikes, Aura of Life, Death Ward, Prayer of Healing")
        if level >= 8:
            parts.append("Guardian of Faith, Ability Score Improvement")
        if level >= 9:
            parts.append("Greater Restoration, Mass Cure Wounds, Flame Strike, Insect Plague")
        if level >= 10:
            parts.append("Divine Intervention, Contagion, Spare the Dying")
        if level >= 11:
            parts.append("Heal, sixth-level Inflict Wounds and Mass Cure Wounds upcasts")
        parts.append("Equipment")
        return ", ".join(parts)
    except Exception:
        logger.exception("Failed to build Cleric source summary at level %s.", level)
        raise
