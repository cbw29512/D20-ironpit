from __future__ import annotations

from app.domain.capability_attacks import ChargeDamageDefinition, ChargeProfileDefinition
from app.domain.weapons import DamageType

_PROFILE_KEYS = frozenset({"minimum_move_ft", "bonus_damage", "prone_save_ability", "prone_save_dc"})
_DAMAGE_KEYS = frozenset({"damage_bonus", "damage_type", "dice_count", "dice_size"})
_ABILITIES = frozenset({"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"})


def supports_charge_profile_2014(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _PROFILE_KEYS:
        return False
    damage = value.get("bonus_damage")
    if not isinstance(damage, dict) or set(damage) != _DAMAGE_KEYS:
        return False
    ability = value.get("prone_save_ability")
    dc = value.get("prone_save_dc")
    return (
        isinstance(value.get("minimum_move_ft"), int) and int(value["minimum_move_ft"]) >= 0
        and isinstance(damage["dice_count"], int) and int(damage["dice_count"]) > 0
        and isinstance(damage["dice_size"], int) and int(damage["dice_size"]) >= 2
        and isinstance(damage["damage_bonus"], int)
        and str(damage["damage_type"]).lower() in {item.value for item in DamageType}
        and ((ability is None and dc is None) or (
            str(ability).lower() in _ABILITIES and isinstance(dc, int) and 0 < int(dc) <= 40
        ))
    )


def charge_profile_2014(value: object) -> ChargeProfileDefinition | None:
    if value in (None, {}):
        return None
    if not supports_charge_profile_2014(value):
        raise ValueError("Unsupported 2014 Charge profile shape.")
    assert isinstance(value, dict)
    damage = value["bonus_damage"]
    assert isinstance(damage, dict)
    ability = value.get("prone_save_ability")
    return ChargeProfileDefinition(
        minimum_move_ft=int(value["minimum_move_ft"]),
        prone_save_ability=str(ability).lower() if ability is not None else None,
        prone_save_dc=int(value["prone_save_dc"]) if value.get("prone_save_dc") is not None else None,
        bonus_damage=ChargeDamageDefinition(
            dice_count=int(damage["dice_count"]), dice_size=int(damage["dice_size"]),
            damage_bonus=int(damage["damage_bonus"]),
            damage_type=DamageType(str(damage["damage_type"]).lower()),
        ),
    )
