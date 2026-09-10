from __future__ import annotations

from app.combat.condition_rules import has_condition
from app.domain.runtime import CombatantState

BLINDED_EFFECT_ID = "blinded"
INVISIBLE_EFFECT_ID = "invisible"


def has_line_of_sight(
    observer: CombatantState,
    target: CombatantState,
    *,
    externally_blocked: bool = False,
) -> bool:
    """Resolve currently certified Iron Pit visibility for one observer/target pair."""
    if externally_blocked:
        return False
    if has_condition(observer, BLINDED_EFFECT_ID):
        return False
    if has_condition(target, INVISIBLE_EFFECT_ID):
        return False
    return True
