from __future__ import annotations

from app.combat.bloodied import is_bloodied
from app.combat.zero_hp import restore_hit_points
from app.domain.models import CombatantState


def _ability_modifier(score: int) -> int:
    return (score - 10) // 2


def bloodied_start_turn_healing_amount(state: CombatantState) -> int:
    features = state.template.progression_features
    amount = features.bloodied_start_turn_healing_base
    if amount <= 0:
        return 0
    if features.bloodied_start_turn_healing_add_constitution:
        scores = state.template.ability_scores
        if scores is None:
            raise ValueError("Constitution-based start-turn healing requires ability scores.")
        amount += _ability_modifier(scores.constitution)
    return max(0, amount)


def resolve_bloodied_start_turn_healing(state: CombatantState) -> int:
    """Resolve declarative start-turn healing that applies only while alive and Bloodied."""
    if state.is_dead or state.current_hp <= 0 or not is_bloodied(state):
        return 0
    amount = bloodied_start_turn_healing_amount(state)
    return restore_hit_points(state, amount) if amount else 0
