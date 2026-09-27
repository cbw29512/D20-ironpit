from __future__ import annotations

from app.domain.damage_sources import DamageSourceQualifier
from app.domain.models import DamageType
from app.domain.progression import ProgressionCombatFeatures
from app.domain.progression_primitives import (
    DelayedResourceRefill,
    ResourceBackedD20BonusDie,
    ResourceBackedOnHitExile,
    SelectableDamageResistance,
    SourceReducesHostileToZeroHpTemporaryHp,
)


def build_warlock_fiend_2014_features(level: int, pact_slot_level: int) -> ProgressionCombatFeatures:
    return ProgressionCombatFeatures(
        source_reduces_hostile_to_zero_hp_temporary_hp=SourceReducesHostileToZeroHpTemporaryHp(
            source_id="dark-ones-blessing",
            source_name="Dark One's Blessing",
            ability="charisma",
            per_level=1,
            minimum=1,
        ),
        selectable_damage_resistance=(
            SelectableDamageResistance(
                source_id="fiendish-resilience",
                source_name="Fiendish Resilience",
                allowed_damage_types=list(DamageType),
                forbidden_source_qualifiers=[
                    DamageSourceQualifier.MAGICAL,
                    DamageSourceQualifier.SILVERED,
                ],
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
                return_damage_dice_count=10,
                return_damage_dice_size=10,
                return_damage_type=DamageType.PSYCHIC,
                return_damage_excluded_creature_types=["fiend"],
            ) if level >= 14 else None
        ),
        delayed_resource_refill=(
            DelayedResourceRefill(
                source_id="eldritch-master",
                source_name="Eldritch Master",
                resource_ids=[f"spell-slot-{pact_slot_level}"],
                use_resource_id="eldritch-master",
                use_resource_cost=1,
                delay_rounds=10,
            ) if level >= 20 else None
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
    )
