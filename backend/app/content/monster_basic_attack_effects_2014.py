from __future__ import annotations

from typing import get_args

from app.content.monster_charge_profile_2014 import supports_charge_profile_2014
from app.content.monster_conditional_damage_2014 import (
    conditional_damage_effect_2014,
    supports_conditional_damage_2014,
)
from app.content.monster_source_2014 import SourceAttack2014
from app.content.monster_zero_hp_save_rider_2014 import (
    ZERO_HP_SAVE_RIDER_KEYS_2014,
    supports_zero_hp_save_rider_2014,
    zero_hp_save_rider_2014,
)
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
from app.domain.action_types import ConditionName, ConditionTiming
from app.domain.weapons import ConditionalAttackAdvantage, DamageType

_DAMAGE_TYPES = frozenset(item.value for item in DamageType)
_DAMAGE_KEYS = frozenset({"average", "bonus", "dice_count", "dice_size", "type"})
_CONTROL_KEYS = frozenset({"grapple_escape_dc", "max_target_size", "restrains_while_grappled"})
_SAVE_CONDITION_KEYS = frozenset({
    "condition_id", "dc", "max_target_size", "save_ability",
    "duration_rounds", "repeat_save_timing", "repeat_save_failure_condition_id", "failure_push_ft",
    "excluded_creature_types", "excluded_creature_subtypes",
})
_SAVE_DAMAGE_KEYS = frozenset({
    "damage_bonus", "damage_dice_count", "damage_dice_size", "damage_type", "dc", "save_ability", "success_damage",
}) | ZERO_HP_SAVE_RIDER_KEYS_2014
_ABILITIES = frozenset({"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"})
_CONDITIONS = frozenset(get_args(ConditionName))
_TIMINGS = frozenset(get_args(ConditionTiming))
_ADVANTAGE_TRIGGERS = frozenset({"target_grappled_by_self"})


def _supported_damage_row(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _DAMAGE_KEYS:
        return False
    damage_type = str(value.get("type", "")).lower()
    return (
        isinstance(value.get("dice_count"), int) and int(value["dice_count"]) > 0
        and isinstance(value.get("dice_size"), int) and int(value["dice_size"]) >= 2
        and isinstance(value.get("bonus", 0), int) and damage_type in _DAMAGE_TYPES
    )


def _supported_control(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _CONTROL_KEYS:
        return False
    max_size = value.get("max_target_size")
    return (
        isinstance(value.get("grapple_escape_dc"), int) and int(value["grapple_escape_dc"]) > 0
        and isinstance(value.get("restrains_while_grappled", False), bool)
        and (max_size is None or str(max_size).lower() in {item.value for item in CreatureSize})
    )


def _optional_size(value: object) -> bool:
    return value is None or str(value).lower() in {item.value for item in CreatureSize}


def _optional_name_list(value: object) -> bool:
    return value is None or (
        isinstance(value, list)
        and all(isinstance(item, str) and str(item).strip() for item in value)
    )


def _supported_save_condition(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _SAVE_CONDITION_KEYS:
        return False
    duration = value.get("duration_rounds")
    timing = value.get("repeat_save_timing")
    escalation = value.get("repeat_save_failure_condition_id")
    if timing is not None and duration is None and escalation is None:
        return False
    if escalation is not None and (
        timing is None or str(escalation).lower() not in _CONDITIONS
    ):
        return False
    push = value.get("failure_push_ft", 0)
    if not isinstance(push, int) or push < 0 or push % 5:
        return False
    return (
        str(value.get("condition_id", "")).lower() in _CONDITIONS
        and isinstance(value.get("dc"), int) and 0 < int(value["dc"]) <= 40
        and str(value.get("save_ability", "")).lower() in _ABILITIES
        and _optional_size(value.get("max_target_size"))
        and (duration is None or (isinstance(duration, int) and 0 < int(duration) <= 100800))
        and (timing is None or str(timing).lower() in _TIMINGS)
        and _optional_name_list(value.get("excluded_creature_types"))
        and _optional_name_list(value.get("excluded_creature_subtypes"))
    )


def _supported_save_damage(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _SAVE_DAMAGE_KEYS:
        return False
    required = {"damage_dice_count", "damage_dice_size", "damage_type", "dc", "save_ability", "success_damage"}
    return (
        required <= set(value)
        and isinstance(value["damage_dice_count"], int) and int(value["damage_dice_count"]) > 0
        and isinstance(value["damage_dice_size"], int) and int(value["damage_dice_size"]) >= 2
        and isinstance(value.get("damage_bonus", 0), int)
        and str(value["damage_type"]).lower() in _DAMAGE_TYPES
        and isinstance(value["dc"], int) and 0 < int(value["dc"]) <= 40
        and str(value["save_ability"]).lower() in _ABILITIES
        and value["success_damage"] in {"none", "half"}
        and supports_zero_hp_save_rider_2014(value)
    )


def _supported_save_max_hp_reduction(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    allowed = {
        "save_ability", "dc", "max_hp_reduction_equals_damage_taken", "zero_max_hp_kills",
    }
    if not set(value) <= allowed or value.get("max_hp_reduction_equals_damage_taken") is not True:
        return False
    return (
        str(value.get("save_ability", "")).lower() in _ABILITIES
        and isinstance(value.get("dc"), int) and 0 < int(value["dc"]) <= 40
        and isinstance(value.get("zero_max_hp_kills", False), bool)
    )


def _supported_contested_movement(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    if set(value) != {"source_ability", "target_ability", "max_target_size", "distance_ft", "direction"}:
        return False
    return (
        str(value["source_ability"]).lower() in _ABILITIES
        and str(value["target_ability"]).lower() in _ABILITIES
        and _optional_size(value.get("max_target_size"))
        and isinstance(value["distance_ft"], int)
        and int(value["distance_ft"]) >= 0
        and int(value["distance_ft"]) % 5 == 0
        and value["direction"] in {"toward_source", "away_from_source"}
    )


def source_conditional_attack_advantage_2014(attack: SourceAttack2014) -> list[ConditionalAttackAdvantage]:
    specs: list[ConditionalAttackAdvantage] = []
    for value in attack.conditional_attack_advantage:
        if not isinstance(value, dict) or set(value) != {"trigger"}:
            raise ValueError(f"{attack.id} has unsupported conditional attack Advantage data")
        trigger = str(value["trigger"]).lower()
        if trigger not in _ADVANTAGE_TRIGGERS:
            raise ValueError(f"{attack.id} has unsupported conditional attack Advantage trigger {trigger!r}")
        specs.append(ConditionalAttackAdvantage(trigger=trigger))
    return specs


def supports_basic_attack_effects_2014(attack: SourceAttack2014) -> bool:
    try:
        source_conditional_attack_advantage_2014(attack)
    except ValueError:
        return False
    if attack.conditional_damage and not all(supports_conditional_damage_2014(row) for row in attack.conditional_damage):
        return False
    if attack.on_hit_save_effect is not None and not (
        _supported_save_condition(attack.on_hit_save_effect)
        or _supported_save_damage(attack.on_hit_save_effect)
        or _supported_save_max_hp_reduction(attack.on_hit_save_effect)
    ):
        return False
    if attack.on_hit_contested_movement is not None and not _supported_contested_movement(
        attack.on_hit_contested_movement
    ):
        return False
    if attack.ongoing_damage_effect:
        return False
    if attack.resource_id or attack.breakable_restraint:
        return False
    if attack.charge_profile is not None and not supports_charge_profile_2014(attack.charge_profile):
        return False
    if attack.grapple_target_policy != "normal":
        return False
    if attack.on_hit_damage and not all(_supported_damage_row(row) for row in attack.on_hit_damage):
        return False
    if attack.control_effect is not None and not _supported_control(attack.control_effect):
        return False
    if attack.forbid_target_grappled_by_self and attack.control_effect is None:
        return False
    return True


def basic_attack_effects_2014(attack: SourceAttack2014) -> list[AttackEffectDefinition]:
    if not supports_basic_attack_effects_2014(attack):
        raise ValueError(f"{attack.id} has unsupported 2014 attack effects")
    effects: list[AttackEffectDefinition] = [
        conditional_damage_effect_2014(row, attack.name) for row in attack.conditional_damage
    ]
    for row in attack.on_hit_damage:
        assert isinstance(row, dict)
        effects.append(DamageEffectDefinition(
            source=attack.name,
            dice=DiceSpec(count=int(row["dice_count"]), size=int(row["dice_size"]), bonus=int(row.get("bonus", 0))),
            damage_type=DamageType(str(row["type"]).lower()),
        ))
    if attack.on_hit_save_effect is not None:
        row = attack.on_hit_save_effect
        assert isinstance(row, dict)
        if _supported_save_max_hp_reduction(row):
            effects.append(SaveMaximumHpReductionEffectDefinition(
                save_ability=str(row["save_ability"]).lower(),
                dc=int(row["dc"]),
                reduction="damage_taken",
                zero_max_hp_kills=bool(row.get("zero_max_hp_kills", False)),
            ))
        elif _supported_save_condition(row):
            max_size = row.get("max_target_size")
            duration = row.get("duration_rounds")
            timing = row.get("repeat_save_timing")
            effects.append(SaveConditionEffectDefinition(
                save_ability=str(row["save_ability"]).lower(), dc=int(row["dc"]),
                condition=str(row["condition_id"]).lower(),
                max_target_size=CreatureSize(str(max_size).lower()) if max_size is not None else None,
                duration_rounds=int(duration) if duration is not None else None,
                repeat_save_timing=str(timing).lower() if timing is not None else None,
                repeat_save_failure_condition=(
                    str(row["repeat_save_failure_condition_id"]).lower()
                    if row.get("repeat_save_failure_condition_id") is not None else None
                ),
                failure_push_ft=int(row.get("failure_push_ft", 0)),
                excluded_creature_types=[str(item) for item in row.get("excluded_creature_types") or []],
                excluded_creature_subtypes=[str(item) for item in row.get("excluded_creature_subtypes") or []],
            ))
        else:
            effects.append(SaveDamageEffectDefinition(
                source=attack.name, save_ability=str(row["save_ability"]).lower(), dc=int(row["dc"]),
                dice=DiceSpec(count=int(row["damage_dice_count"]), size=int(row["damage_dice_size"]), bonus=int(row.get("damage_bonus", 0))),
                damage_type=DamageType(str(row["damage_type"]).lower()), success_damage=str(row["success_damage"]),
                zero_hp_rider=zero_hp_save_rider_2014(row),
            ))
    if attack.on_hit_contested_movement is not None:
        row = attack.on_hit_contested_movement
        assert isinstance(row, dict)
        max_size = row.get("max_target_size")
        effects.append(ContestedMovementEffectDefinition(
            source_ability=str(row["source_ability"]).lower(),
            target_ability=str(row["target_ability"]).lower(),
            max_target_size=CreatureSize(str(max_size).lower()) if max_size is not None else None,
            distance_ft=int(row["distance_ft"]),
            direction=str(row["direction"]),
        ))
    if attack.control_effect is not None:
        row = attack.control_effect
        assert isinstance(row, dict)
        max_size = row.get("max_target_size")
        effects.append(GrappleEffectDefinition(
            escape_dc=int(row["grapple_escape_dc"]),
            max_target_size=CreatureSize(str(max_size).lower()) if max_size is not None else None,
            restrains=bool(row.get("restrains_while_grappled", False)),
        ))
    return effects
