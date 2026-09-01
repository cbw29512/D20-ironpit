from __future__ import annotations

from app.combat.barbarian import rage_active
from app.combat.reckless_attack import reckless_attack_active
from app.domain.models import CombatantState, DamageType, WeaponAttack

FRENZY_FEATURE_ID = "frenzy"
_FRENZY_RECKLESS_MARKER = "frenzy-reckless"
BonusDamageSpec = tuple[str, int, int, DamageType]


def mark_reckless_use_while_raging(state: CombatantState, turn_key: str | None) -> None:
    """Record that Reckless Attack was chosen this turn while Rage was already active."""
    if turn_key is None or not state.template.progression_features.frenzy or not rage_active(state):
        return
    state.feature_last_turn_keys[_FRENZY_RECKLESS_MARKER] = turn_key


def frenzy_bonus_damage(
    state: CombatantState,
    attack: WeaponAttack,
    turn_key: str | None,
) -> BonusDamageSpec | None:
    """Consume Frenzy on the first qualifying hit of the marked turn."""
    if (
        turn_key is None
        or not state.template.progression_features.frenzy
        or not rage_active(state)
        or not reckless_attack_active(state)
        or attack.attack_ability != "strength"
        or state.feature_last_turn_keys.get(_FRENZY_RECKLESS_MARKER) != turn_key
        or state.feature_last_turn_keys.get(FRENZY_FEATURE_ID) == turn_key
    ):
        return None
    dice_count = state.template.rage_damage_bonus
    if dice_count <= 0:
        return None
    state.feature_last_turn_keys[FRENZY_FEATURE_ID] = turn_key
    return ("Frenzy", dice_count, 6, attack.weapon.damage_type)
