from __future__ import annotations

import logging

from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.healing_riders import OutgoingHealingDiceMaximizer
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant, SlotHealingSelfRider

logger = logging.getLogger(__name__)
_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def build_cleric_progression_2014(level: int) -> ProgressionCombatFeatures:
    try:
        return ProgressionCombatFeatures(
            turning_failure_destroy_max_cr=(
                "4" if level >= 17 else "3" if level >= 14 else "2" if level >= 11
                else "1" if level >= 8 else "1/2" if level >= 5 else None
            ),
            slot_healing_other_self_rider=(
                SlotHealingSelfRider(source_id="blessed-healer", flat_bonus=2, per_slot_level=1)
                if level >= 6 else None
            ),
            outgoing_healing_dice_maximizer=(
                OutgoingHealingDiceMaximizer(
                    source_id="supreme-healing",
                    source_name="Supreme Healing",
                )
                if level >= 17 else None
            ),
            once_per_turn_weapon_hit_damage_rider=(
                OncePerTurnWeaponHitDamageRider(
                    source_id="divine-strike",
                    source_name="Divine Strike",
                    dice_count=2 if level >= 14 else 1,
                    dice_size=8,
                    damage_type="radiant",
                )
                if level >= 8 else None
            ),
            saving_throw_advantage_grants=[
                SavingThrowAdvantageGrant(
                    source_id="dwarven-resilience",
                    source_name="Dwarven Resilience",
                    abilities=_ABILITIES,
                    required_effect_tags=["poison"],
                )
            ],
        )
    except Exception:
        logger.exception("Failed to build 2014 Cleric progression features at level %s.", level)
        raise
