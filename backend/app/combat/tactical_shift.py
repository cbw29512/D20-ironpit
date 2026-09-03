from __future__ import annotations

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_tactical_shift(
    sequence: int,
    round_number: int,
    fighter: EncounterCombatant,
    setup: EncounterSetup,
) -> BattleEvent | None:
    """Fixed Iron Pit formation abstracts Tactical Shift movement and never relocates a card."""
    return None
