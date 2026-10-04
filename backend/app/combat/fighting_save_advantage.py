from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def sides_are_fighting(
    caster: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup | None,
) -> bool:
    """True when the caster or a living ally is fighting the target in this encounter."""
    try:
        if setup is None or caster.side == target.side:
            return False
        allies = setup.heroes if caster.side == "heroes" else setup.monsters
        return any(
            ally.state.is_alive and not ally.state.is_dead and ally.state.current_hp > 0
            for ally in allies
        )
    except Exception:
        logger.exception("Failed to evaluate fighting-save Advantage for %s.", caster.combatant_id)
        raise
