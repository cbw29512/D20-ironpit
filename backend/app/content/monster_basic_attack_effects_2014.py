from __future__ import annotations

from app.content.monster_source_2014 import SourceAttack2014
from app.domain.capability_effects import (
    AttackEffectDefinition,
    DamageEffectDefinition,
    DiceSpec,
    GrappleEffectDefinition,
    SaveConditionEffectDefinition,
    SaveDamageEffectDefinition,
)
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

_DAMAGE_TYPES = frozenset(item.value for item in DamageType)
_DAMAGE_KEYS = frozenset({"average", "bonus", "dice_count", "dice_size", "type"})
_CONTROL_KEYS = frozenset({"grapple_escape_dc", "max_target_size", "restrains_while_grappled"})
_SAVE_CONDITION_KEYS = frozenset({"condition_id", "dc", "max_target_size", "save_ability"})
_SAVE_DAMAGE_KEYS = frozenset({
    "damage_bonus", "damage_dice_count", "damage_dice_size", "damage_type", "dc", "save_ability", "success_damage",
})
_ABILITIES = frozenset({"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"})


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


def _supported_save_condition(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _SAVE_CONDITION_KEYS:
        return False
    max_size = value.get("max_target_size")
    return (
        value.get("condition_id") == "prone"
        and isinstance(value.get("dc"), int) and 0 < int(value["dc"]) <= 40
        and str(value.get("save_ability", "")).lower() in _ABILITIES
        and (max_size is None or str(max_size).lower() in {item.value for item in CreatureSize})
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
    )


def supports_basic_attack_effects_2014(attack: SourceAttack2014) -> bool:
    if attack.conditional_damage or attack.conditional_attack_advantage:
        return False
    if attack.on_hit_save_effect is not None and not (
        _supported_save_condition(attack.on_hit_save_effect) or _supported_save_damage(attack.on_hit_save_effect)
    ):
        return False
    if attack.on_hit_contested_movement or attack.ongoing_damage_effect:
        return False
    if attack.resource_id or attack.breakable_restraint or attack.charge_profile:
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
    effects: list[AttackEffectDefinition] = []
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
        if _supported_save_condition(row):
            max_size = row.get("max_target_size")
            effects.append(SaveConditionEffectDefinition(
                save_ability=str(row["save_ability"]).lower(), dc=int(row["dc"]), condition="prone",
                max_target_size=CreatureSize(str(max_size).lower()) if max_size is not None else None,
            ))
        else:
            effects.append(SaveDamageEffectDefinition(
                source=attack.name, save_ability=str(row["save_ability"]).lower(), dc=int(row["dc"]),
                dice=DiceSpec(count=int(row["damage_dice_count"]), size=int(row["damage_dice_size"]), bonus=int(row.get("damage_bonus", 0))),
                damage_type=DamageType(str(row["damage_type"]).lower()), success_damage=str(row["success_damage"]),
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
