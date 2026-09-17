from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.character_builds import AbilityScores
from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def martial_arts_die(level: int) -> int:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Monk attack helpers cover levels 1 through 10.")
        return 4 if level < 5 else 6
    except Exception:
        logger.exception("Failed to resolve 2014 Monk Martial Arts die at level %s", level)
        raise


def build_unarmed_attack(level: int, scores: AbilityScores) -> WeaponAttack:
    try:
        dexterity = scores.modifier("dexterity")
        weapon = Weapon(
            id="unarmed-strike",
            name="Unarmed Strike",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=martial_arts_die(level),
            damage_type=DamageType.BLUDGEONING,
            animation="strike",
            reach_ft=5,
        )
        return WeaponAttack(
            id="kael-2014-unarmed",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build 2014 Monk unarmed attack at level %s", level)
        raise


def build_shortsword_attack(level: int, scores: AbilityScores) -> WeaponAttack:
    try:
        dexterity = scores.modifier("dexterity")
        weapon = build_weapon("shortsword").model_copy(update={"mastery_property": None})
        return WeaponAttack(
            id="kael-2014-shortsword",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build 2014 Monk shortsword attack at level %s", level)
        raise


def build_extra_attack(level: int) -> AttackActionDefinition | None:
    try:
        if level < 5:
            return None
        choices = ["kael-2014-unarmed", "kael-2014-shortsword"]
        return AttackActionDefinition(
            id="extra-attack",
            name="Extra Attack",
            slots=[
                AttackActionSlot(attack_ids=choices),
                AttackActionSlot(attack_ids=choices),
            ],
            is_attack_action=True,
        )
    except Exception:
        logger.exception("Failed to build 2014 Monk Extra Attack at level %s", level)
        raise
