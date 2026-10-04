from __future__ import annotations

import logging

from app.domain.models import DamageType
from app.domain.progression import ProgressionCombatFeatures
from app.domain.progression_primitives import (
    DelayedResourceRefill,
    ResourceBackedD20BonusDie,
    ResourceBackedOnHitExile,
    SelectableDamageResistance,
    SourceReducesHostileToZeroHpTemporaryHp,
)
from app.domain.d20_outcome_adjustments import ResourceBackedD20OutcomeAdjustment

logger = logging.getLogger(__name__)


def build_warlock_fiend_2024_features(
    level: int,
    pact_slot_level: int,
    proficiency_bonus: int,
    charisma_modifier: int,
) -> ProgressionCombatFeatures:
    try:
        return ProgressionCombatFeatures(
            source_reduces_hostile_to_zero_hp_temporary_hp=(
                SourceReducesHostileToZeroHpTemporaryHp(
                    source_id="dark-ones-blessing",
                    source_name="Dark One's Blessing",
                    ability="charisma",
                    per_level=1,
                    minimum=1,
                    ally_zero_hp_range_ft=10,
                ) if level >= 3 else None
            ),
            selectable_damage_resistance=(
                SelectableDamageResistance(
                    source_id="fiendish-resilience",
                    source_name="Fiendish Resilience",
                    allowed_damage_types=[
                        item for item in DamageType if item != DamageType.FORCE
                    ],
                    forbidden_source_qualifiers=[],
                    priority=90,
                ) if level >= 10 else None
            ),
            resource_backed_on_hit_exile=(
                ResourceBackedOnHitExile(
                    source_id="hurl-through-hell",
                    source_name="Hurl Through Hell",
                    resource_id="hurl-through-hell",
                    resource_cost=1,
                    expiry_timing="source_turn_end",
                    duration_rounds=1,
                    save_ability="charisma",
                    save_dc=8 + proficiency_bonus + charisma_modifier,
                    once_per_turn=True,
                    hit_damage_dice_count=8,
                    hit_damage_dice_size=10,
                    hit_damage_type=DamageType.PSYCHIC,
                    hit_damage_excluded_creature_types=["fiend"],
                    apply_condition_ids=["incapacitated"],
                ) if level >= 14 else None
            ),
            delayed_resource_refill=(
                DelayedResourceRefill(
                    source_id="magical-cunning",
                    source_name="Magical Cunning",
                    resource_ids=[f"spell-slot-{pact_slot_level}"],
                    use_resource_id="magical-cunning",
                    use_resource_cost=1,
                    delay_rounds=10,
                    restore_mode="max" if level >= 20 else "half_max_rounded_up",
                ) if level >= 2 else None
            ),
            resource_backed_d20_bonus_dice=(
                [ResourceBackedD20BonusDie(
                    source_id="dark-ones-own-luck",
                    source_name="Dark One's Own Luck",
                    resource_id="dark-ones-own-luck",
                    resource_cost=1,
                    dice_count=1,
                    dice_size=10,
                    test_kinds=["saving_throw", "ability_check"],
                )] if level >= 6 else []
            ),
            resource_backed_d20_outcome_adjustments=(
                [ResourceBackedD20OutcomeAdjustment(
                    source_id="boon-of-fate",
                    source_name="Boon of Fate",
                    resource_id="boon-of-fate",
                    dice_count=2,
                    dice_size=4,
                    range_ft=60,
                    test_kinds=["attack", "saving_throw", "ability_check"],
                    can_add=True,
                    can_subtract=True,
                )] if level >= 19 else []
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Fiend Warlock features at level %s.", level)
        raise
