from __future__ import annotations

import logging

from app.content.monster_attack_effect_validation_2014 import (
    supported_save_condition_2014,
    supported_save_max_hp_reduction_2014,
)
from app.content.monster_hp_loss_effect_2014 import (
    ongoing_hp_loss_effect_2014,
    supported_ongoing_hp_loss_2014,
)
from app.content.monster_save_persistent_validation_2014 import (
    supported_save_persistent_2014,
)
from app.content.monster_source_2014 import SourceAttack2014
from app.content.monster_zero_hp_save_rider_2014 import zero_hp_save_rider_2014
from app.domain.capability_effects import (
    AttackEffectDefinition,
    DiceSpec,
    SaveConditionEffectDefinition,
    SaveDamageEffectDefinition,
    SaveMaximumHpReductionEffectDefinition,
    SavePersistentEffectDefinition,
)
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)


def save_effect_2014(attack: SourceAttack2014) -> AttackEffectDefinition:
    try:
        row = attack.on_hit_save_effect
        if not isinstance(row, dict):
            raise ValueError(f"{attack.id} has no source save-effect row.")
        if supported_ongoing_hp_loss_2014(attack):
            return ongoing_hp_loss_effect_2014(attack)
        if supported_save_max_hp_reduction_2014(row):
            return SaveMaximumHpReductionEffectDefinition(
                save_ability=str(row["save_ability"]).lower(),
                dc=int(row["dc"]),
                reduction="damage_taken",
                zero_max_hp_kills=bool(row.get("zero_max_hp_kills", False)),
            )
        if supported_save_persistent_2014(row):
            return SavePersistentEffectDefinition(
                save_ability=str(row["save_ability"]).lower(),
                dc=int(row["dc"]),
                effect_id=str(row["effect_id"]),
                curse_id=str(row["curse_id"]),
                cannot_regain_hit_points=bool(row["cannot_regain_hit_points"]),
                allowed_removal_action_ids=list(row["allowed_removal_action_ids"]),
            )
        if supported_save_condition_2014(row):
            max_size = row.get("max_target_size")
            duration = row.get("duration_rounds")
            timing = row.get("repeat_save_timing")
            return SaveConditionEffectDefinition(
                save_ability=str(row["save_ability"]).lower(),
                dc=int(row["dc"]),
                condition=str(row["condition_id"]).lower(),
                max_target_size=(
                    CreatureSize(str(max_size).lower()) if max_size is not None else None
                ),
                duration_rounds=int(duration) if duration is not None else None,
                repeat_save_timing=str(timing).lower() if timing is not None else None,
                repeat_save_failure_condition=(
                    str(row["repeat_save_failure_condition_id"]).lower()
                    if row.get("repeat_save_failure_condition_id") is not None else None
                ),
                failure_push_ft=int(row.get("failure_push_ft", 0)),
                cannot_regain_hit_points=bool(
                    row.get("cannot_regain_hit_points", False)
                ),
                start_of_turn_damage_dice_count=int(
                    row.get("start_of_turn_damage_dice_count", 0)
                ),
                start_of_turn_damage_dice_size=int(
                    row.get("start_of_turn_damage_dice_size", 6)
                ),
                start_of_turn_damage_type=(
                    DamageType(str(row["start_of_turn_damage_type"]).lower())
                    if row.get("start_of_turn_damage_type") is not None else None
                ),
                failure_margin_escalation=row.get("failure_margin_escalation"),
                excluded_creature_types=[
                    str(item) for item in row.get("excluded_creature_types") or []
                ],
                excluded_creature_subtypes=[
                    str(item) for item in row.get("excluded_creature_subtypes") or []
                ],
            )
        return SaveDamageEffectDefinition(
            source=attack.name,
            save_ability=str(row["save_ability"]).lower(),
            dc=int(row["dc"]),
            dice=DiceSpec(
                count=int(row["damage_dice_count"]),
                size=int(row["damage_dice_size"]),
                bonus=int(row.get("damage_bonus", 0)),
            ),
            damage_type=DamageType(str(row["damage_type"]).lower()),
            success_damage=str(row["success_damage"]),
            zero_hp_rider=zero_hp_save_rider_2014(row),
        )
    except Exception:
        logger.exception("Failed to compile 2014 save effect for %s.", attack.id)
        raise
