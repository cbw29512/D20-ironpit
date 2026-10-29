"""Fight-local accounting for effects triggered by damage from a swallowed victim.

Monster cards provide the threshold; this module only accumulates observed
post-defense damage by the correct source in the current encounter turn.
"""
from __future__ import annotations

from app.domain.swallowed_state import SwallowedState


def record_swallowed_victim_damage(
    effect: SwallowedState, *, victim_id: str, attacker_id: str,
    owner_id: str, actual_damage: int, turn_key: str,
) -> int:
    """Return the accumulated damage, or zero for an unrelated attacker."""
    if not turn_key:
        raise ValueError("Swallowed damage requires an encounter turn key")
    if actual_damage < 0:
        raise ValueError("Actual damage cannot be negative")
    if effect.source_id != owner_id or victim_id != attacker_id:
        return 0
    if effect.damage_tracking_turn_key != turn_key:
        effect.damage_tracking_turn_key = turn_key
        effect.damage_from_victim_this_turn = 0
    effect.damage_from_victim_this_turn += actual_damage
    return effect.damage_from_victim_this_turn


def swallowed_regurgitation_ready(effect: SwallowedState) -> bool:
    threshold = effect.regurgitation_damage_threshold
    return threshold is not None and effect.damage_from_victim_this_turn >= threshold
