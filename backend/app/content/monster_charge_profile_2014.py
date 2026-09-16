from __future__ import annotations

from app.domain.capability_attacks import ChargeDamageDefinition, ChargeProfileDefinition
from app.domain.weapons import DamageType

_PROFILE_KEYS = frozenset({
    "minimum_move_ft", "bonus_damage", "prone_save_ability", "prone_save_dc", "follow_up_attack_id",
})
_DAMAGE_KEYS = frozenset({"damage_bonus", "damage_type", "dice_count", "dice_size"})
_ABILITIES = frozenset({"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"})


def _supports_damage(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, dict) or set(value) != _DAMAGE_KEYS:
        return False
    return (
        isinstance(value["dice_count"], int) and int(value["dice_count"]) > 0
        and isinstance(value["dice_size"], int) and int(value["dice_size"]) >= 2
        and isinstance(value["damage_bonus"], int)
        and str(value["damage_type"]).lower() in {item.value for item in DamageType}
    )


def supports_charge_profile_2014(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _PROFILE_KEYS:
        return False
    ability = value.get("prone_save_ability")
    dc = value.get("prone_save_dc")
    follow_up = value.get("follow_up_attack_id")
    return (
        isinstance(value.get("minimum_move_ft"), int) and int(value["minimum_move_ft"]) >= 0
        and _supports_damage(value.get("bonus_damage"))
        and ((ability is None and dc is None) or (
            str(ability).lower() in _ABILITIES and isinstance(dc, int) and 0 < int(dc) <= 40
        ))
        and (follow_up is None or (isinstance(follow_up, str) and bool(follow_up.strip())))
    )


def charge_profile_2014(value: object, *, monster_id: str | None = None) -> ChargeProfileDefinition | None:
    if value in (None, {}):
        return None
    if not supports_charge_profile_2014(value):
        raise ValueError("Unsupported 2014 Charge profile shape.")
    assert isinstance(value, dict)
    damage = value.get("bonus_damage")
    ability = value.get("prone_save_ability")
    follow_up = value.get("follow_up_attack_id")
    runtime_follow_up = None
    if follow_up is not None:
        if monster_id is None:
            raise ValueError("2014 Charge follow-up requires monster id for runtime attack binding.")
        runtime_follow_up = f"2014-{monster_id}-{follow_up}".replace("--", "-")
    return ChargeProfileDefinition(
        minimum_move_ft=int(value["minimum_move_ft"]),
        prone_save_ability=str(ability).lower() if ability is not None else None,
        prone_save_dc=int(value["prone_save_dc"]) if value.get("prone_save_dc") is not None else None,
        bonus_damage=(
            ChargeDamageDefinition(
                dice_count=int(damage["dice_count"]), dice_size=int(damage["dice_size"]),
                damage_bonus=int(damage["damage_bonus"]),
                damage_type=DamageType(str(damage["damage_type"]).lower()),
            ) if isinstance(damage, dict) else None
        ),
        follow_up_attack_id=runtime_follow_up,
        follow_up_required_target_condition="prone" if runtime_follow_up else None,
        follow_up_action_cost="bonus_action" if runtime_follow_up else "free",
    )
