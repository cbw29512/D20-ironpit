from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.condition_rules import BLINDED, has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.opportunity_attack_rules import opportunity_attack_weapon
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def _swap_would_provoke(defender: EncounterCombatant, ally: EncounterCombatant, setup: EncounterSetup) -> bool:
    opponents = setup.monsters if defender.side == "heroes" else setup.heroes
    return any(
        opportunity_attack_weapon(
            reactor, defender,
            combatant_distance(reactor, defender), abs(reactor.position_ft - ally.position_ft), "reaction",
        ) is not None
        for reactor in opponents
    )


def select_redirect_ally(defender: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    """Use the nearest stable-ID legal ally only when the optional swap does not provoke an OA."""
    try:
        reaction = defender.state.template.redirect_attack_reaction
        if reaction is None or not is_available(defender.state, "reaction") or has_condition(defender.state, BLINDED):
            return None
        allies = setup.heroes if defender.side == "heroes" else setup.monsters
        candidates = [
            ally for ally in allies
            if ally.combatant_id != defender.combatant_id
            and ally.state.is_alive and not ally.state.is_dead
            and size_at_most(ally.state.template.size, reaction.ally_max_size)
            and combatant_distance(defender, ally) <= reaction.ally_range_ft
            and not _swap_would_provoke(defender, ally, setup)
        ]
        return min(candidates, key=lambda ally: (combatant_distance(defender, ally), ally.combatant_id), default=None)
    except Exception as exc:
        logger.exception("Redirect Attack ally selection failed for %s.", defender.combatant_id)
        raise RuntimeError("Redirect Attack ally could not be selected.") from exc


def swap_redirect_positions(defender: EncounterCombatant, ally: EncounterCombatant) -> None:
    defender.position_ft, ally.position_ft = ally.position_ft, defender.position_ft
