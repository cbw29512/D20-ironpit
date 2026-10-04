from __future__ import annotations

import logging

from app.content.monk_2024_resource_rules import monk_martial_arts_die
from app.domain.bonus_action_follow_up import BonusActionFollowUpTacticalGrant
from app.domain.end_turn_condition_removal import EndTurnConditionRemovalGrant
from app.domain.on_hit_save_riders import ResourceBackedOnHitSaveRider
from app.domain.progression import (
    DamageResistanceBypassGrant,
    DeferredSaveEffect,
    FailedSaveRerollGrant,
    NaturalTwentyAttackDamageGrant,
    ProgressionCombatFeatures,
    SavingThrowProficiencyGrant,
)

logger = logging.getLogger(__name__)


def build_monk_2024_progression(
    level: int,
    unarmed_attack_id: str,
    proficiency_bonus: int,
    wisdom_modifier: int,
) -> ProgressionCombatFeatures:
    """Bind 2024 Monk features to existing universal progression primitives."""
    try:
        return ProgressionCombatFeatures(
            damage_resistance_bypass_grants=(
                [DamageResistanceBypassGrant(
                    source_id="boon-irresistible-offense",
                    source_name="Boon of Irresistible Offense",
                    damage_types=["bludgeoning", "piercing", "slashing"],
                )]
                if level >= 19 else []
            ),
            natural_twenty_attack_damage_grants=(
                [NaturalTwentyAttackDamageGrant(
                    source_id="boon-irresistible-offense",
                    source_name="Boon of Irresistible Offense",
                    ability="dexterity",
                    damage_type_source="attack",
                )]
                if level >= 19 else []
            ),
            evasion=level >= 7,
            evasion_disabled_while_incapacitated=level >= 7,
            bonus_action_follow_up_tactical_grants=(
                [
                    BonusActionFollowUpTacticalGrant(
                        source_id="fleet-step",
                        source_name="Fleet Step",
                        tactical_grant_id="step-of-the-wind-dash",
                        excluded_trigger_ids=[
                            "step-of-the-wind-dash",
                            "step-of-the-wind-focus",
                            "fleet-step",
                        ],
                    )
                ]
                if level >= 11 else []
            ),
            end_turn_condition_removal=(
                EndTurnConditionRemovalGrant(
                    source_id="self-restoration",
                    source_name="Self-Restoration",
                    condition_ids=["charmed", "frightened", "poisoned"],
                    max_conditions=1,
                )
                if level >= 10 else None
            ),
            martial_arts_bonus_attack=True,
            martial_arts_die_size=monk_martial_arts_die(level),
            stunning_strike=level >= 5,
            resource_backed_on_hit_save_rider=(
                ResourceBackedOnHitSaveRider(
                    source_id="stunning-strike",
                    source_name="Stunning Strike",
                    trigger_attack_ids=[unarmed_attack_id],
                    resource_id="focus-points",
                    resource_cost=1,
                    save_ability="constitution",
                    save_dc=8 + proficiency_bonus + wisdom_modifier,
                    once_per_turn=True,
                    failed_condition_id="stunned",
                    failed_condition_expiry_timing="source_turn_start",
                    successful_save_speed_multiplier=0.5,
                    successful_save_next_attack_advantage=True,
                )
                if level >= 5 else None
            ),
            saving_throw_proficiency_grants=(
                [
                    SavingThrowProficiencyGrant(
                        source_id="disciplined-survivor",
                        abilities=["constitution", "intelligence", "wisdom", "charisma"],
                    )
                ]
                if level >= 14 else []
            ),
            failed_save_reroll_grants=(
                [
                    FailedSaveRerollGrant(
                        source_id="disciplined-survivor",
                        source_name="Disciplined Survivor",
                        resource_id="focus-points",
                        resource_cost=1,
                    )
                ]
                if level >= 14 else []
            ),
            deferred_save_effect=(
                DeferredSaveEffect(
                    source_id="quivering-palm",
                    source_name="Quivering Palm",
                    trigger_weapon_ids=["unarmed-strike"],
                    resource_id="focus-points",
                    resource_cost=4,
                    save_ability="constitution",
                    save_dc=8 + proficiency_bonus + wisdom_modifier,
                    failure_damage_dice_count=10,
                    failure_damage_dice_size=12,
                    failure_damage_type="force",
                    success_damage_from_failure="half",
                    allow_attack_slot_activation=True,
                    allow_harmless_end_on_rearm=True,
                    max_active_targets=1,
                )
                if level >= 17 else None
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Monk progression features at level %s.", level)
        raise
