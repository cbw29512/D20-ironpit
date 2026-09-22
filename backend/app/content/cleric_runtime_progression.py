from __future__ import annotations

from app.domain.progression import (
    AbilityScaledDamageRider,
    ProgressionCombatFeatures,
    SlotHealingSelfRider,
)
from app.domain.progression_riders import DamagingActionTemporaryHpRider


def build_seraphine_progression_features(level: int) -> ProgressionCombatFeatures:
    return ProgressionCombatFeatures(
        turning_failure_damage=(
            AbilityScaledDamageRider(
                source_id="sear-undead",
                ability="wisdom",
                dice_size=8,
                damage_type="radiant",
            )
            if level >= 5 else None
        ),
        slot_healing_other_self_rider=(
            SlotHealingSelfRider(
                source_id="blessed-healer",
                flat_bonus=2,
                per_slot_level=1,
            )
            if level >= 6 else None
        ),
        damaging_action_temporary_hp_rider=(
            DamagingActionTemporaryHpRider(
                source_id="improved-blessed-strikes",
                action_ids=["sacred-flame"],
                ability="wisdom",
                multiplier=2,
            )
            if level >= 14 else None
        ),
    )
