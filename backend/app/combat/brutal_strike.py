from __future__ import annotations

from app.combat.reckless_attack import reckless_attack_active
from app.domain.models import CombatantState, DamageType, WeaponAttack

BRUTAL_STRIKE_FEATURE_ID = "brutal-strike"
BRUTAL_STRIKE_PENDING_KEY = "brutal-strike-pending"
BRUTAL_STRIKE_HIT_KEY = "brutal-strike-hit"
BonusDamageSpec = tuple[str, int, int, DamageType]


def _eligible_for_brutal_strike(
    state: CombatantState, attack: WeaponAttack, turn_key: str | None, *, has_disadvantage: bool,
) -> bool:
    return bool(
        state.template.ruleset != "2014"
        and state.template.progression_features.brutal_strike_damage_dice > 0
        and turn_key is not None
        and not has_disadvantage
        and attack.attack_ability == "strength"
        and reckless_attack_active(state)
        and state.feature_last_turn_keys.get(BRUTAL_STRIKE_FEATURE_ID) != turn_key
    )


def brutal_strike_bonus_damage(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    *,
    has_disadvantage: bool,
) -> BonusDamageSpec | None:
    """Resolve damage only for the attack roll that actually chose Brutal Strike."""
    if turn_key is None:
        return None
    pending = state.feature_last_turn_keys.get(BRUTAL_STRIKE_PENDING_KEY) == turn_key
    if not pending:
        if not _eligible_for_brutal_strike(state, attack, turn_key, has_disadvantage=has_disadvantage):
            return None
        state.feature_last_turn_keys[BRUTAL_STRIKE_FEATURE_ID] = turn_key
    state.feature_last_turn_keys.pop(BRUTAL_STRIKE_PENDING_KEY, None)
    state.feature_last_turn_keys[BRUTAL_STRIKE_HIT_KEY] = turn_key
    dice_count = state.template.progression_features.brutal_strike_damage_dice
    return ("Brutal Strike", dice_count, 10, attack.weapon.damage_type)


def brutal_strike_advantage_suppression(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    *,
    has_disadvantage: bool,
) -> int:
    """Choose Brutal Strike on this roll and spend the once-per-turn choice before the d20 is rolled."""
    if not _eligible_for_brutal_strike(state, attack, turn_key, has_disadvantage=has_disadvantage):
        return 0
    assert turn_key is not None
    state.feature_last_turn_keys[BRUTAL_STRIKE_FEATURE_ID] = turn_key
    state.feature_last_turn_keys[BRUTAL_STRIKE_PENDING_KEY] = turn_key
    return 1


def clear_brutal_strike_pending(state: CombatantState, turn_key: str | None) -> bool:
    if turn_key is None or state.feature_last_turn_keys.get(BRUTAL_STRIKE_PENDING_KEY) != turn_key:
        return False
    state.feature_last_turn_keys.pop(BRUTAL_STRIKE_PENDING_KEY, None)
    return True


def brutal_strike_hit_on_turn(state: CombatantState, turn_key: str | None) -> bool:
    return bool(turn_key and state.feature_last_turn_keys.get(BRUTAL_STRIKE_HIT_KEY) == turn_key)

def brutal_strike_attack_sources(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
    *,
    reckless_advantage: int,
    disadvantage_sources: int,
) -> tuple[int, bool]:
    """Return adjusted Reckless Advantage and whether the chosen roll has Disadvantage."""
    has_disadvantage = disadvantage_sources > 0
    suppression = brutal_strike_advantage_suppression(
        state, attack, turn_key, has_disadvantage=has_disadvantage,
    )
    return max(0, reckless_advantage - suppression), has_disadvantage
