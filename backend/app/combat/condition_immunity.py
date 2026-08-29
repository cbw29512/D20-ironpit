from __future__ import annotations

from app.domain.models import CombatantState


def condition_is_immune(state: CombatantState, condition_id: str) -> bool:
    return condition_id in state.template.condition_immunities
