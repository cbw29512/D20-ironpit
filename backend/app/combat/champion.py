from __future__ import annotations

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def apply_critical_closing_move(
    attacker: EncounterCombatant,
    setup: EncounterSetup | None,
    event: BattleEvent,
) -> BattleEvent:
    """Fixed Iron Pit formation abstracts Remarkable Athlete movement; the attack result is unchanged."""
    return event
