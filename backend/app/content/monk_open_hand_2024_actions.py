from __future__ import annotations

import logging

from app.content.monk_2024_resource_rules import monk_martial_arts_die
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.models import DamageType, WeaponAttack
from app.domain.reactions import AttackDamageReductionReaction
from app.domain.tactical_actions import BonusActionTacticalGrant
from app.domain.weapons import OnHitConditionSave

logger = logging.getLogger(__name__)


def build_monk_bonus_attacks(
    level: int,
    unarmed: WeaponAttack,
    proficiency_bonus: int,
    wisdom_modifier: int,
) -> list[BonusAttackGrant]:
    try:
        grants: list[BonusAttackGrant] = []
        if level >= 2:
            grants.append(BonusAttackGrant(
                id="flurry-of-blows",
                name="Flurry of Blows",
                attack_ids=[unarmed.id],
                attack_count=3 if level >= 10 else 2,
                resource_id="focus-points",
                resource_cost=1,
                priority=80,
                on_hit_condition_save=(
                    OnHitConditionSave(
                        save_ability="dexterity",
                        dc=8 + proficiency_bonus + wisdom_modifier,
                        condition_id="prone",
                    )
                    if level >= 3 else None
                ),
            ))
        grants.append(BonusAttackGrant(
            id="martial-arts",
            name="Martial Arts",
            attack_ids=[unarmed.id],
            attack_count=1,
            priority=90,
        ))
        return grants
    except Exception:
        logger.exception("Failed to build 2024 Monk bonus attacks at level %s.", level)
        raise


def build_monk_tactical_actions(level: int) -> list[BonusActionTacticalGrant]:
    try:
        if level < 2:
            return []
        return [
            BonusActionTacticalGrant(
                id="step-of-the-wind-dash",
                name="Step of the Wind",
                effects=["dash"],
                priority=40,
                use_policy="enable-offense",
            ),
            BonusActionTacticalGrant(
                id="patient-defense-disengage",
                name="Patient Defense",
                effects=["disengage"],
                priority=100,
                use_policy="manual",
            ),
            BonusActionTacticalGrant(
                id="patient-defense-focus",
                name="Patient Defense",
                effects=["disengage", "dodge"],
                resource_id="focus-points",
                resource_cost=1,
                priority=90,
                use_policy="defensive-fallback",
                temporary_hp_dice_count=2 if level >= 10 else 0,
                temporary_hp_dice_size=monk_martial_arts_die(level) if level >= 10 else 0,
            ),
            BonusActionTacticalGrant(
                id="step-of-the-wind-focus",
                name="Step of the Wind",
                effects=["disengage", "dash"],
                resource_id="focus-points",
                resource_cost=1,
                priority=100,
                use_policy="manual",
                jump_distance_multiplier=2,
            ),
        ]
    except Exception:
        logger.exception("Failed to build 2024 Monk tactical actions at level %s.", level)
        raise


def build_monk_attack_damage_reduction(level: int) -> AttackDamageReductionReaction | None:
    try:
        if level < 3:
            return None
        return AttackDamageReductionReaction(
            source_id="deflect-attacks",
            source_name="Deflect Attacks",
            attack_kinds=["melee", "ranged"],
            required_damage_types=[DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING],
            reduction_dice_count=1,
            reduction_dice_size=10,
            reduction_ability="dexterity",
            add_level=True,
        )
    except Exception:
        logger.exception("Failed to build 2024 Deflect Attacks binding at level %s.", level)
        raise
