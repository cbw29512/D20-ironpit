from __future__ import annotations

from app.content.monster_attack_effect_validation_2014 import (
    ADVANTAGE_TRIGGERS_2014,
    supported_contested_movement_2014,
    supported_control_2014,
    supported_damage_row_2014,
    supported_save_condition_2014,
    supported_save_damage_2014,
    supported_save_max_hp_reduction_2014,
)
from app.content.monster_charge_profile_2014 import supports_charge_profile_2014
from app.content.monster_conditional_damage_2014 import (
    conditional_damage_effect_2014,
    supports_conditional_damage_2014,
)
from app.content.monster_source_2014 import SourceAttack2014
from app.content.monster_zero_hp_save_rider_2014 import zero_hp_save_rider_2014
from app.domain.capability_effects import (
    AttackEffectDefinition,
    ContestedMovementEffectDefinition,
    DamageEffectDefinition,
    DiceSpec,
    GrappleEffectDefinition,
    SaveConditionEffectDefinition,
    SaveDamageEffectDefinition,
    SaveMaximumHpReductionEffectDefinition,
)
from app.domain.size import CreatureSize
from app.domain.weapons import ConditionalAttackAdvantage, DamageType


def source_conditional_attack_advantage_2014(
    attack: SourceAttack2014,
) -> list[ConditionalAttackAdvantage]:
    specs: list[ConditionalAttackAdvantage] = []
    for value in attack.conditional_attack_advantage:
        if not isinstance(value, dict) or set(value) != {"trigger"}:
            raise ValueError(f"{attack.id} has unsupported conditional attack Advantage data")
        trigger = str(value["trigger"]).lower()
        if trigger not in ADVANTAGE_TRIGGERS_2014:
            raise ValueError(
                f"{attack.id} has unsupported conditional attack Advantage trigger {trigger!r}"
            )
        specs.append(ConditionalAttackAdvantage(trigger=trigger))
    return specs


def supports_basic_attack_effects_2014(attack: SourceAttack2014) -> bool:
    try:
        source_conditional_attack_advantage_2014(attack)
    except ValueError:
        return False
    if attack.conditional_damage and not all(
        supports_conditional_damage_2014(row) for row in attack.conditional_damage
    ):
        return False
    if attack.on_hit_save_effect is not None and not (
        supported_save_condition_2014(attack.on_hit_save_effect)
        or supported_save_damage_2014(attack.on_hit_save_effect)
        or supported_save_max_hp_reduction_2014(attack.on_hit_save_effect)
    ):
        return False
    if (
        attack.on_hit_contested_movement is not None
        and not supported_contested_movement_2014(attack.on_hit_contested_movement)
    ):
        return False
    if attack.ongoing_damage_effect or attack.resource_id or attack.breakable_restraint:
        return False
    if (
        attack.charge_profile is not None
        and not supports_charge_profile_2014(attack.charge_profile)
    ):
        return False
    if attack.grapple_target_policy not in {"normal", "own_grapple_only"}:
        return False
    if attack.on_hit_damage and not all(
        supported_damage_row_2014(row) for row in attack.on_hit_damage
    ):
        return False
    if attack.control_effect is not None and not supported_control_2014(
        attack.control_effect
    ):
        return False
    return not (attack.forbid_target_grappled_by_self and attack.control_effect is None)


def _save_effect_2014(attack: SourceAttack2014) -> AttackEffectDefinition:
    row = attack.on_hit_save_effect
    assert isinstance(row, dict)
    if supported_save_max_hp_reduction_2014(row):
        return SaveMaximumHpReductionEffectDefinition(
            save_ability=str(row["save_ability"]).lower(),
            dc=int(row["dc"]),
            reduction="damage_taken",
            zero_max_hp_kills=bool(row.get("zero_max_hp_kills", False)),
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


def basic_attack_effects_2014(attack: SourceAttack2014) -> list[AttackEffectDefinition]:
    if not supports_basic_attack_effects_2014(attack):
        raise ValueError(f"{attack.id} has unsupported 2014 attack effects")
    effects: list[AttackEffectDefinition] = [
        conditional_damage_effect_2014(row, attack.name)
        for row in attack.conditional_damage
    ]
    for row in attack.on_hit_damage:
        assert isinstance(row, dict)
        effects.append(DamageEffectDefinition(
            source=attack.name,
            dice=DiceSpec(
                count=int(row["dice_count"]),
                size=int(row["dice_size"]),
                bonus=int(row.get("bonus", 0)),
            ),
            damage_type=DamageType(str(row["type"]).lower()),
        ))
    if attack.on_hit_save_effect is not None:
        effects.append(_save_effect_2014(attack))
    if attack.on_hit_contested_movement is not None:
        row = attack.on_hit_contested_movement
        assert isinstance(row, dict)
        max_size = row.get("max_target_size")
        effects.append(ContestedMovementEffectDefinition(
            source_ability=str(row["source_ability"]).lower(),
            target_ability=str(row["target_ability"]).lower(),
            max_target_size=(
                CreatureSize(str(max_size).lower()) if max_size is not None else None
            ),
            distance_ft=int(row["distance_ft"]),
            direction=str(row["direction"]),
        ))
    if attack.control_effect is not None:
        row = attack.control_effect
        assert isinstance(row, dict)
        max_size = row.get("max_target_size")
        effects.append(GrappleEffectDefinition(
            escape_dc=int(row["grapple_escape_dc"]),
            max_target_size=(
                CreatureSize(str(max_size).lower()) if max_size is not None else None
            ),
            restrains=bool(row.get("restrains_while_grappled", False)),
        ))
    return effects
