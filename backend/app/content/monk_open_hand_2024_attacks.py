from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.character_builds import AbilityScores
from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def build_kael_unarmed_attack_2024(level: int, scores: AbilityScores) -> WeaponAttack:
    """Build Kael's 2024 Dexterity-based Unarmed Strike using the current Martial Arts die."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            raise ValueError("The current 2024 Monk attack tranche supports levels 1-9 only.")
        dexterity = scores.modifier("dexterity")
        weapon = Weapon(
            id="unarmed-strike",
            name="Unarmed Strike",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=8 if level >= 5 else 6,
            damage_type=DamageType.BLUDGEONING,
            damage_type_choices=[DamageType.FORCE] if level >= 6 else [],
            animation="strike",
            reach_ft=5,
        )
        return WeaponAttack(
            id="kael-2024-unarmed",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build 2024 Kael unarmed attack at level %s.", level)
        raise


def build_kael_extra_attack_2024(level: int, attack_id: str) -> AttackActionDefinition | None:
    """Reuse the shared Attack-action slot model for 2024 Extra Attack."""
    try:
        if level < 5:
            return None
        return AttackActionDefinition(
            id="extra-attack",
            name="Extra Attack",
            slots=[
                AttackActionSlot(attack_ids=[attack_id]),
                AttackActionSlot(attack_ids=[attack_id]),
            ],
            is_attack_action=True,
        )
    except Exception:
        logger.exception("Failed to build 2024 Kael Extra Attack at level %s.", level)
        raise
