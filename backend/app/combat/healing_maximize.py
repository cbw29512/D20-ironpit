from __future__ import annotations

import logging

from app.combat.defensive_modifier_rules import healing_is_maximized
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def healing_dice_are_maximized(
    healer: EncounterCombatant,
    target: EncounterCombatant,
) -> bool:
    """Combine source-owned outgoing and recipient-owned healing maximizers."""
    try:
        outgoing = healer.state.template.progression_features.outgoing_healing_dice_maximizer
        return outgoing is not None or healing_is_maximized(target.state)
    except Exception as exc:
        logger.exception(
            "Failed healing-maximization resolution for %s healing %s.",
            healer.state.template.name,
            target.state.template.name,
        )
        raise RuntimeError("Healing maximization could not be resolved.") from exc
