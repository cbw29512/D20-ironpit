from __future__ import annotations

from app.domain.models import CombatantState


def strength_d20_disadvantage(state: CombatantState) -> int:
    """Return one disadvantage source when any active timed effect penalizes Strength d20 tests."""
    return int(any(effect.disadvantage_strength_d20_tests for effect in state.timed_effects))
