from __future__ import annotations

from app.domain.capability_effects import DamageEffectDefinition, DiceSpec
from app.domain.weapons import DamageType

_CONDITIONAL_DAMAGE_KEYS = frozenset({
    "trigger", "mode", "dice_count", "dice_size", "damage_bonus", "damage_type",
})
_CONDITIONAL_TRIGGERS = frozenset({"attack_advantage", "attacker_bloodied", "target_bloodied"})
_CONDITIONAL_MODES = frozenset({"add", "replace_weapon"})
_DAMAGE_TYPES = frozenset(item.value for item in DamageType)


def supports_conditional_damage_2014(value: object) -> bool:
    if not isinstance(value, dict) or not set(value) <= _CONDITIONAL_DAMAGE_KEYS:
        return False
    return (
        str(value.get("trigger", "")) in _CONDITIONAL_TRIGGERS
        and str(value.get("mode", "add")) in _CONDITIONAL_MODES
        and isinstance(value.get("dice_count"), int) and int(value["dice_count"]) > 0
        and isinstance(value.get("dice_size"), int) and int(value["dice_size"]) >= 2
        and isinstance(value.get("damage_bonus", 0), int)
        and str(value.get("damage_type", "")).lower() in _DAMAGE_TYPES
    )


def conditional_damage_effect_2014(value: object, source: str) -> DamageEffectDefinition:
    if not supports_conditional_damage_2014(value):
        raise ValueError(f"Unsupported 2014 conditional damage row for {source!r}: {value!r}")
    assert isinstance(value, dict)
    return DamageEffectDefinition(
        source=source,
        dice=DiceSpec(
            count=int(value["dice_count"]),
            size=int(value["dice_size"]),
            bonus=int(value.get("damage_bonus", 0)),
        ),
        damage_type=DamageType(str(value["damage_type"]).lower()),
        trigger=str(value["trigger"]),
        mode=str(value.get("mode", "add")),
    )
