from __future__ import annotations

import logging

from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.domain.progression import (
    AbilityScaledDamageRider,
    ProgressionCombatFeatures,
    SlotHealingSelfRider,
)
from app.domain.progression_riders import DamagingActionTemporaryHpRider

logger = logging.getLogger(__name__)

_MAXIMIZED_LIFE_HEALING_SOURCES = [
    "cure-wounds", "healing-word", "mass-healing-word", "mass-cure-wounds",
    "divine-intervention-mass-cure-wounds", "mass-cure-wounds-l6",
    "mass-cure-wounds-l7", "mass-cure-wounds-l8", "mass-cure-wounds-l9",
    "divine-spark",
]


def build_seraphine_progression_features(level: int) -> ProgressionCombatFeatures:
    try:
        row = CLERIC_COMBAT_LEVELS[level]
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
            feature_dice_counts={"divine-spark": row.divine_spark_dice} if level >= 2 else {},
            maximized_healing_source_ids=(
                list(_MAXIMIZED_LIFE_HEALING_SOURCES) if level >= 17 else []
            ),
        )
    except Exception:
        logger.exception("Failed to compile Seraphine progression features at level %s.", level)
        raise
