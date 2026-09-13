from __future__ import annotations

from app.domain.models import CombatantState, DamageType, RollMode, WeaponAttack
from app.domain.traits import CombatTrait

SNEAK_ATTACK_FEATURE_ID = "sneak-attack"
MARTIAL_ADVANTAGE_FEATURE_ID = "martial-advantage"
SneakDamageSpec = tuple[str, int, int, DamageType]


def sneak_attack_bonus_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    attack_mode: RollMode,
    turn_key: str | None,
    ally_adjacent_to_target: bool,
) -> SneakDamageSpec | None:
    """Return and consume RAW Sneak Attack when this hit qualifies in Iron Pit."""
    dice_count = attacker.template.progression_features.sneak_attack_d6
    if dice_count <= 0 or not attack.sneak_attack_eligible:
        return None
    if attack_mode is RollMode.DISADVANTAGE:
        return None
    if attack_mode is not RollMode.ADVANTAGE and not ally_adjacent_to_target:
        return None
    if turn_key is None:
        raise ValueError("Sneak Attack requires the actual active-turn key for once-per-turn tracking.")
    if attacker.feature_last_turn_keys.get(SNEAK_ATTACK_FEATURE_ID) == turn_key:
        return None
    attacker.feature_last_turn_keys[SNEAK_ATTACK_FEATURE_ID] = turn_key
    return ("Sneak Attack", dice_count, 6, attack.weapon.damage_type)


def martial_advantage_bonus_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    ally_adjacent_to_target: bool,
) -> SneakDamageSpec | None:
    if CombatTrait.MARTIAL_ADVANTAGE not in attacker.template.combat_traits or not ally_adjacent_to_target:
        return None
    if attack.weapon.damage_type is None:
        return None
    if turn_key is None:
        raise ValueError("Martial Advantage requires the actual active-turn key for once-per-turn tracking.")
    if attacker.feature_last_turn_keys.get(MARTIAL_ADVANTAGE_FEATURE_ID) == turn_key:
        return None
    attacker.feature_last_turn_keys[MARTIAL_ADVANTAGE_FEATURE_ID] = turn_key
    return ("Martial Advantage", 2, 6, attack.weapon.damage_type)
