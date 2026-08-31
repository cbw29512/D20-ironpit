from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def select_redirect_ally(defender: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    """Iron Pit policy: use the nearest stable-ID legal ally whenever Redirect Attack can trigger."""
    try:
        reaction = defender.state.template.redirect_attack_reaction
        if reaction is None or not is_available(defender.state, "reaction"):
            return None
        allies = setup.heroes if defender.side == "heroes" else setup.monsters
        candidates = [
            ally for ally in allies
            if ally.combatant_id != defender.combatant_id
            and ally.state.is_alive and not ally.state.is_dead and ally.state.current_hp > 0
            and size_at_most(ally.state.template.size, reaction.ally_max_size)
            and combatant_distance(defender, ally) <= reaction.ally_range_ft
        ]
        return min(candidates, key=lambda ally: (combatant_distance(defender, ally), ally.combatant_id), default=None)
    except Exception as exc:
        logger.exception("Redirect Attack ally selection failed for %s.", defender.combatant_id)
        raise RuntimeError("Redirect Attack ally could not be selected.") from exc


def swap_redirect_positions(defender: EncounterCombatant, ally: EncounterCombatant) -> None:
    defender.position_ft, ally.position_ft = ally.position_ft, defender.position_ft
