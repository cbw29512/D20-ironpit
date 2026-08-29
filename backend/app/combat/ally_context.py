from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance
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


def pack_tactics_active(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
) -> bool:
    """Return whether the attacker has a qualifying ally within 5 feet of the target."""
    try:
        if CombatTrait.PACK_TACTICS not in attacker.state.template.combat_traits:
            return False
        return any(combatant_distance(ally, target) <= 5 for ally in active_allies(attacker, setup))
    except Exception as exc:
        logger.exception("Pack Tactics evaluation failed for %s.", attacker.combatant_id)
        raise RuntimeError("Pack Tactics could not be evaluated.") from exc
