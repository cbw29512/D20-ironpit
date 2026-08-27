from __future__ import annotations

import logging

from app.content.srd_attacks import (
    build_ogre_greatclub_attack,
    build_ogre_javelin_attack,
    build_skeleton_shortbow_attack,
    build_skeleton_shortsword_attack,
)
from app.content.srd_humanoids import build_knight, build_tough_boss
from app.domain.models import Ability, CombatantTemplate, ConditionType, DamageType, SizeCategory, VisualLoadout

logger = logging.getLogger(__name__)


def build_skeleton() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-skeleton",
            name="Skeleton",
            archetype="Skeleton",
            challenge_rating="1/4",
            kind="monster",
            size=SizeCategory.MEDIUM,
            armor_class=14,
            max_hp=13,
            speed_ft=30,
            initiative_bonus=3,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 0,
                Ability.DEXTERITY: 3,
                Ability.CONSTITUTION: 2,
                Ability.INTELLIGENCE: -2,
                Ability.WISDOM: -1,
                Ability.CHARISMA: -3,
            },
            damage_vulnerabilities=[DamageType.BLUDGEONING],
            damage_immunities=[DamageType.POISON],
            condition_immunities=[ConditionType.POISONED],
            weapon_attack=build_skeleton_shortsword_attack(),
            alternate_weapon_attacks=[build_skeleton_shortbow_attack()],
            visual=VisualLoadout(
                armor="none",
                main_hand="shortsword",
                body_style="skeleton",
            ),
            source="SRD 5.2.1 Skeleton",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Skeleton.")
        raise RuntimeError("Skeleton could not be created.") from exc


def build_ogre() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-ogre",
            name="Ogre",
            archetype="Ogre",
            challenge_rating="2",
            kind="monster",
            size=SizeCategory.LARGE,
            armor_class=11,
            max_hp=68,
            speed_ft=40,
            initiative_bonus=-1,
            weapon_attack=build_ogre_greatclub_attack(),
            alternate_weapon_attacks=[build_ogre_javelin_attack()],
            visual=VisualLoadout(
                armor="none",
                main_hand="greatclub",
                body_style="giant",
            ),
            source="SRD 5.2.1 Ogre",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Ogre.")
        raise RuntimeError("Ogre could not be created.") from exc


__all__ = ["build_knight", "build_ogre", "build_skeleton", "build_tough_boss"]
