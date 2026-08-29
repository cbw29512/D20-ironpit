from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterOutcome, EncounterSetup

logger = logging.getLogger(__name__)


def _side_defeated(combatants: list[EncounterCombatant]) -> bool:
    return all(member.state.current_hp <= 0 or not member.state.is_alive for member in combatants)


def resolve_encounter_outcome(setup: EncounterSetup) -> EncounterOutcome:
    """Return the side-level outcome without inventing recovery or death rules."""
    try:
        heroes_down = _side_defeated(setup.heroes)
        monsters_down = _side_defeated(setup.monsters)
        if heroes_down and monsters_down:
            return "draw"
        if monsters_down:
            return "heroes_win"
        if heroes_down:
            return "monsters_win"
        return "active"
    except Exception as exc:
        logger.exception("Encounter outcome check failed.")
        raise RuntimeError("Encounter outcome could not be resolved.") from exc
