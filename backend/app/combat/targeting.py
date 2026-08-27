from __future__ import annotations

import logging

from app.domain.encounters import EncounterParticipantState, EncounterState, distance_between

logger = logging.getLogger(__name__)


def select_nearest_enemy(
    encounter: EncounterState,
    actor: EncounterParticipantState,
) -> EncounterParticipantState | None:
    """Simple baseline policy: nearest living enemy, then stable instance id."""
    try:
        enemies = encounter.enemies_of(actor)
        if not enemies:
            return None
        return min(
            enemies,
            key=lambda target: (distance_between(actor, target), target.combatant.instance_id),
        )
    except Exception as exc:
        logger.exception("Encounter target selection failed for %s.", actor.combatant.instance_id)
        raise RuntimeError("Target could not be selected.") from exc
