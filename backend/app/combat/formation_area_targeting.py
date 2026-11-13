"""Formation-only cone targeting, independent of the 24x16 display.

Shape is still a source-owned capability. The formation policy treats an
unobstructed cone as attacking the opposing exposed front rank; back-rank
members are not included until their frontline collapses. Actual cone
length/angle remain immutable card data and are not measured on the display.
"""
from __future__ import annotations

import logging

from app.combat.formation_engagement import effective_row
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def cone_frontline_targets(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    area: AreaTargeting,
) -> tuple[str, ...]:
    try:
        if setup.arena_mode != "formation" or area.shape != "cone":
            raise ValueError("Formation cone targeting needs a standard Pit cone.")
        candidates = setup.monsters if actor.side == "heroes" else setup.heroes
        return tuple(
            item.combatant_id for item in candidates
            if item.state.is_alive and not item.state.is_dead
            and item.state.current_hp > 0
            and effective_row(item, setup) == "front"
        )
    except Exception:
        logger.exception("Failed formation cone targeting for %s.", actor.combatant_id)
        raise
