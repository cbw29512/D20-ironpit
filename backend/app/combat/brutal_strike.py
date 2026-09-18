from __future__ import annotations

from app.combat.reckless_attack import reckless_attack_active
from app.domain.models import CombatantState, DamageType, WeaponAttack

BRUTAL_STRIKE_FEATURE_ID = "brutal-strike"
BonusDamageSpec = tuple[str, int, int, DamageType]


def brutal_strike_bonus_damage(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    *,
    has_disadvantage: bool,
) -> BonusDamageSpec | None:
    """Consume 2024 Brutal Strike on one eligible Strength attack during the active turn."""
    dice_count = state.template.progression_features.brutal_strike_damage_dice
    if (
        state.template.ruleset == "2014"
        or dice_count <= 0
        or turn_key is None
        or has_disadvantage
        or attack.attack_ability != "strength"
        or not reckless_attack_active(state)
        or state.feature_last_turn_keys.get(BRUTAL_STRIKE_FEATURE_ID) == turn_key
    ):
        return None
    state.feature_last_turn_keys[BRUTAL_STRIKE_FEATURE_ID] = turn_key
    return ("Brutal Strike", dice_count, 10, attack.weapon.damage_type)
