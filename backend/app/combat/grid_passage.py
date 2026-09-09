from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.domain.encounters import EncounterCombatant
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_SIZE_RANK = {
    CreatureSize.TINY: 0,
    CreatureSize.SMALL: 1,
    CreatureSize.MEDIUM: 2,
    CreatureSize.LARGE: 3,
    CreatureSize.HUGE: 4,
    CreatureSize.GARGANTUAN: 5,
}


def can_pass_through(mover: EncounterCombatant, occupant: EncounterCombatant) -> bool:
    """Return whether SRD 5.2.1 permits the mover to pass through this creature's space."""
    try:
        if mover.combatant_id == occupant.combatant_id:
            return True
        if mover.side == occupant.side:
            return True
        if is_incapacitated(occupant.state):
            return True
        if occupant.state.template.size is CreatureSize.TINY:
            return True
        mover_rank = _SIZE_RANK[mover.state.template.size]
        occupant_rank = _SIZE_RANK[occupant.state.template.size]
        return abs(mover_rank - occupant_rank) >= 2
    except Exception:
        logger.exception(
            "Failed to evaluate creature-space passage for mover=%s occupant=%s.",
            mover.combatant_id,
            occupant.combatant_id,
        )
        raise


def creature_space_is_difficult(mover: EncounterCombatant, occupant: EncounterCombatant) -> bool:
    """Return whether entering this otherwise-passable creature space costs Difficult Terrain movement."""
    try:
        if mover.combatant_id == occupant.combatant_id:
            return False
        if mover.side == occupant.side:
            return False
        return occupant.state.template.size is not CreatureSize.TINY
    except Exception:
        logger.exception(
            "Failed to evaluate creature-space movement cost for mover=%s occupant=%s.",
            mover.combatant_id,
            occupant.combatant_id,
        )
        raise
