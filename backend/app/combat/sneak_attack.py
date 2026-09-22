from __future__ import annotations

from app.combat.cunning_strike import select_canonical_die_cost
from app.domain.models import CombatantState, DamageType, RollMode, WeaponAttack

SNEAK_ATTACK_FEATURE_ID = "sneak-attack"
SneakDamageSpec = tuple[str, int, int, DamageType]


def sneak_attack_bonus_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    attack_mode: RollMode,
    turn_key: str | None,
    ally_adjacent_to_target: bool,
    target: CombatantState | None = None,
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
    die_cost = select_canonical_die_cost(attacker, target, turn_key)
    attacker.feature_last_turn_keys[SNEAK_ATTACK_FEATURE_ID] = turn_key
    return ("Sneak Attack", dice_count - die_cost, 6, attack.weapon.damage_type)
