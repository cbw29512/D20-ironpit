from __future__ import annotations

import logging

from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def automatically_fails_save(
    action: SavingThrowAction,
    target: EncounterCombatant,
) -> bool:
    """Return whether source data makes this target automatically fail this save."""
    try:
        target_type = str(target.state.template.creature_type or "").split(" (")[0].strip().casefold()
        failure_types = {
            str(creature_type).strip().casefold()
            for creature_type in action.automatic_failure_creature_types
            if str(creature_type).strip()
        }
        return bool(target_type and target_type in failure_types)
    except Exception:
        logger.exception(
            "Failed to evaluate automatic save failure for action %s against %s.",
            action.id,
            target.combatant_id,
        )
        raise
