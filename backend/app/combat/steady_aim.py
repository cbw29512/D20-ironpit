from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.domain.models import BattleEvent, CombatantState


def use_steady_aim(
    sequence: int,
    round_number: int,
    combatant_id: str,
    state: CombatantState,
) -> BattleEvent | None:
    """Spend the Bonus Action for Steady Aim and report one attack-Advantage source."""
    if not state.template.progression_features.steady_aim or not is_available(state, "bonus_action"):
        return None
    spend(state, "bonus_action")
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=combatant_id,
        actor_name=state.template.name,
        feature_id="steady-aim",
        animation="condition",
        description=f"{state.template.name} uses Steady Aim; the next attack this turn has Advantage.",
    )
