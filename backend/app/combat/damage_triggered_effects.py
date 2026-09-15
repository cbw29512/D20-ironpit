from __future__ import annotations

from app.combat.timed_roll_effects import apply_roll_penalty
from app.domain.models import CombatantState, DamageType


def apply_damage_triggered_effects(
    state: CombatantState,
    amount: int,
    damage_types: set[DamageType],
) -> list[str]:
    """Activate declarative effects after positive post-defense damage is taken."""
    if amount <= 0 or not damage_types:
        return []
    applied: list[str] = []
    for profile in state.template.damage_triggered_roll_penalties:
        if damage_types.isdisjoint(profile.damage_types):
            continue
        applied.append(apply_roll_penalty(
            state,
            effect_id=profile.id,
            attack_roll_disadvantage=profile.attack_roll_disadvantage,
            ability_check_disadvantage=profile.ability_check_disadvantage,
            expires_after_next_target_turn=profile.expires_after_next_target_turn,
        ))
    return applied
