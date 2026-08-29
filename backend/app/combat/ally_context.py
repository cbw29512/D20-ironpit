from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def active_allies(attacker: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    allies = setup.heroes if attacker.side == "heroes" else setup.monsters
    return [
        ally
        for ally in allies
        if ally.combatant_id != attacker.combatant_id
        and ally.state.is_alive
        and not ally.state.is_dead
        and not ally.state.is_unconscious
        and ally.state.current_hp > 0
    ]


def has_adjacent_active_ally(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    """Iron Pit abstraction: any active ally counts as being within 5 feet.

    The card-v-card fight intentionally does not simulate allied formation movement.
    If a side has at least two active combatants, ally-proximity mechanics treat the
    combatants as adjacent to one another.
    """
    return bool(active_allies(attacker, setup))


def pack_tactics_active(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
) -> bool:
    """Return whether Pack Tactics is active under Iron Pit's adjacency abstraction."""
    try:
        del target  # Pack Tactics still targets an enemy; exact ally geometry is abstracted.
        if CombatTrait.PACK_TACTICS not in attacker.state.template.combat_traits:
            return False
        return has_adjacent_active_ally(attacker, setup)
    except Exception as exc:
        logger.exception("Pack Tactics evaluation failed for %s.", attacker.combatant_id)
        raise RuntimeError("Pack Tactics could not be evaluated.") from exc
