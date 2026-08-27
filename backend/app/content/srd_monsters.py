from __future__ import annotations

import logging

from app.content.srd_attacks import (
    build_knight_crossbow_attack,
    build_knight_greatsword_attack,
    build_ogre_greatclub_attack,
    build_ogre_javelin_attack,
    build_skeleton_shortbow_attack,
    build_skeleton_shortsword_attack,
)
from app.content.srd_boss_attacks import (
    build_tough_boss_crossbow_attack,
    build_tough_boss_warhammer_attack,
)
from app.domain.models import CombatantTemplate, DamageType, VisualLoadout

logger = logging.getLogger(__name__)


def build_skeleton() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-skeleton",
            name="Skeleton",
            archetype="Skeleton",
            challenge_rating="1/4",
            kind="monster",
            armor_class=14,
            max_hp=13,
            speed_ft=30,
            initiative_bonus=3,
            damage_vulnerabilities=[DamageType.BLUDGEONING],
            damage_immunities=[DamageType.POISON],
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


def build_knight() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-knight",
            name="Knight",
            archetype="Knight",
            challenge_rating="3",
            kind="monster",
            armor_class=18,
            max_hp=52,
            speed_ft=30,
            initiative_bonus=0,
            attacks_per_action=2,
            weapon_attack=build_knight_greatsword_attack(),
            alternate_weapon_attacks=[build_knight_crossbow_attack()],
            visual=VisualLoadout(
                armor="plate-armor",
                main_hand="greatsword",
                body_style="humanoid",
            ),
            source="SRD 5.2.1 Knight",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Knight.")
        raise RuntimeError("Knight could not be created.") from exc


def build_tough_boss() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-tough-boss",
            name="Tough Boss",
            archetype="Tough Boss",
            challenge_rating="4",
            kind="monster",
            armor_class=16,
            max_hp=82,
            speed_ft=30,
            initiative_bonus=2,
            attacks_per_action=2,
            weapon_attack=build_tough_boss_warhammer_attack(),
            alternate_weapon_attacks=[build_tough_boss_crossbow_attack()],
            visual=VisualLoadout(
                armor="chain-mail",
                main_hand="warhammer",
                body_style="humanoid",
            ),
            source="SRD 5.2.1 Tough Boss",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Tough Boss.")
        raise RuntimeError("Tough Boss could not be created.") from exc
