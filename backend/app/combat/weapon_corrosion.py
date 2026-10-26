"""Fight-only per-weapon corrosion. Source policy decides qualifying weapon hits.

No immutable card or equipment record is ever edited. This is a shared state
primitive; only a separately source-proven combat hook may activate it.
"""
from __future__ import annotations

from app.domain.models import CombatantState

_MAX_PENALTY = 5


def _weapon_key(weapon_id: str) -> str:
    if not isinstance(weapon_id, str) or not weapon_id.strip():
        raise ValueError("Corrosion requires a stable weapon-instance ID.")
    return weapon_id


def corrosion_penalty(state: CombatantState, weapon_id: str) -> int:
    """Negative damage-only adjustment for an individual weapon this fight."""
    key = _weapon_key(weapon_id)
    stacks = state.weapon_corrosion_penalties.get(key, 0)
    if not isinstance(stacks, int) or not 0 <= stacks <= _MAX_PENALTY:
        raise ValueError("Invalid encounter-local weapon corrosion stacks.")
    return -stacks


def weapon_available_after_corrosion(state: CombatantState, weapon_id: str) -> bool:
    return corrosion_penalty(state, weapon_id) > -_MAX_PENALTY


def corrode_weapon_after_hit(
    state: CombatantState, weapon_id: str, *,
    hit: bool, nonmagical_metal: bool,
) -> int:
    """Apply one stack after a qualifying hit; miss/magic/nonmetal do nothing."""
    key = _weapon_key(weapon_id)
    previous = -corrosion_penalty(state, key)
    if not isinstance(hit, bool) or not isinstance(nonmagical_metal, bool):
        raise ValueError("Weapon corrosion requires verified hit and material flags.")
    if not hit or not nonmagical_metal:
        return -previous
    if previous == _MAX_PENALTY:
        raise ValueError("A destroyed weapon cannot land another hit this fight.")
    state.weapon_corrosion_penalties[key] = previous + 1
    return -(previous + 1)


def apply_weapon_corrosion_damage_penalty(
    state: CombatantState, weapon_id: str, rolled_weapon_damage: int,
) -> int:
    """Only reduce the triggering weapon component, never an extra spell rider."""
    if not isinstance(rolled_weapon_damage, int) or rolled_weapon_damage < 0:
        raise ValueError("Weapon damage before corrosion must be nonnegative.")
    if not weapon_available_after_corrosion(state, weapon_id):
        raise ValueError("Destroyed weapon cannot be used for another attack.")
    return max(0, rolled_weapon_damage + corrosion_penalty(state, weapon_id))
