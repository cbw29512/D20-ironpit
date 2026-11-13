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

def line_lane_targets(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    area: AreaTargeting,
) -> tuple[str, ...]:
    """Pick one complete formation lane, not every enemy in the arena.

    The 3-lane deployment order is the stable lane identity. Each lane may
    contain a front and a back combatant. Source line length and width remain
    immutable, but no grid coordinate or foot-distance chooses coverage.
    """
    try:
        if setup.arena_mode != "formation" or area.shape != "line":
            raise ValueError("Formation line targeting needs a standard Pit line.")
        opponents = setup.monsters if actor.side == "heroes" else setup.heroes
        by_lane: dict[int, list[str]] = {0: [], 1: [], 2: []}
        counts = {"front": 0, "back": 0}
        for member in opponents:
            row = member.state.initial_formation_row or member.state.formation_row
            if row not in counts:
                raise ValueError("Line targeting requires assigned initial formation rows.")
            lane = counts[row]
            counts[row] += 1
            if lane >= 3:
                raise ValueError("A formation row cannot contain more than three creatures.")
            if member.state.is_alive and not member.state.is_dead and member.state.current_hp > 0:
                by_lane[lane].append(member.combatant_id)
        # Favor the lane with the greatest real affected target count.
        return tuple(max(by_lane.values(), key=len))
    except Exception:
        logger.exception("Failed formation line targeting for %s.", actor.combatant_id)
        raise
