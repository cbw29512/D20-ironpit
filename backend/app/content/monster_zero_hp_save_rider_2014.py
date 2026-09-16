from __future__ import annotations

from typing import get_args

from app.domain.actions import ConditionName
from app.domain.zero_hp_effects import ZeroHpSaveDamageRider

ZERO_HP_SAVE_RIDER_KEYS_2014 = frozenset({
    "zero_hp_stable", "zero_hp_condition_ids", "zero_hp_duration_rounds",
})
_CONDITIONS = frozenset(get_args(ConditionName))


def supports_zero_hp_save_rider_2014(value: dict) -> bool:
    present = ZERO_HP_SAVE_RIDER_KEYS_2014 & set(value)
    if not present:
        return True
    conditions = value.get("zero_hp_condition_ids")
    return (
        present == ZERO_HP_SAVE_RIDER_KEYS_2014
        and value.get("zero_hp_stable") is True
        and isinstance(conditions, list) and bool(conditions)
        and all(isinstance(item, str) and item in _CONDITIONS for item in conditions)
        and isinstance(value.get("zero_hp_duration_rounds"), int)
        and int(value["zero_hp_duration_rounds"]) > 0
    )


def zero_hp_save_rider_2014(value: dict) -> ZeroHpSaveDamageRider | None:
    if value.get("zero_hp_stable") is not True:
        return None
    return ZeroHpSaveDamageRider(
        stable=True,
        condition_ids=list(value["zero_hp_condition_ids"]),
        duration_rounds=int(value["zero_hp_duration_rounds"]),
    )
