from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterOutcome, EncounterSetup

logger = logging.getLogger(__name__)


def _combatant_defeated(member: EncounterCombatant) -> bool:
    state = member.state
    if state.template.kind == "character":
        return state.is_dead or not state.is_alive
    regeneration = state.template.regeneration
    if (
        state.current_hp <= 0 and regeneration is not None
        and regeneration.delays_death_at_zero and state.is_alive and not state.is_dead
    ):
        return False
    return state.current_hp <= 0 or state.is_dead or not state.is_alive


def _side_defeated(combatants: list[EncounterCombatant]) -> bool:
    return all(_combatant_defeated(member) for member in combatants)


def resolve_encounter_outcome(setup: EncounterSetup) -> EncounterOutcome:
    """Return the deathmatch outcome while preserving delayed Regeneration death checks."""
    try:
        heroes_dead = _side_defeated(setup.heroes)
        monsters_dead = _side_defeated(setup.monsters)
        if heroes_dead and monsters_dead:
            return "draw"
        if monsters_dead:
            return "heroes_win"
        if heroes_dead:
            return "monsters_win"
        return "active"
    except Exception as exc:
        logger.exception("Encounter outcome check failed.")
        raise RuntimeError("Encounter outcome could not be resolved.") from exc
