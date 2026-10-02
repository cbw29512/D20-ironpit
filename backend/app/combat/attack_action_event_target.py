from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def event_target(event: BattleEvent, setup: EncounterSetup) -> EncounterCombatant | None:
    """Resolve an event target from fresh encounter state."""
    try:
        return next(
            (
                member
                for member in [*setup.heroes, *setup.monsters]
                if member.combatant_id == event.target_id
            ),
            None,
        )
    except Exception:
        logger.exception("Failed to resolve event target %s.", event.target_id)
        raise
