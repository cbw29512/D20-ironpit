from __future__ import annotations

from app.combat.damage import BonusDamageSpec
from app.domain.models import CombatantState, RollMode, WeaponAttack

SNEAK_ATTACK_FEATURE_ID = "sneak-attack"


def sneak_attack_bonus_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    attack_mode: RollMode,
    turn_key: str | None,
    ally_adjacent_to_target: bool,
) -> BonusDamageSpec | None:
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
