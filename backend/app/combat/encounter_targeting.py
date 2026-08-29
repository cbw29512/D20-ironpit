from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def combatant_distance(attacker: EncounterCombatant, target: EncounterCombatant) -> int:
    return abs(attacker.position_ft - target.position_ft)


def living_opponents(attacker: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    candidates = setup.monsters if attacker.side == "heroes" else setup.heroes
    return [member for member in candidates if member.state.is_alive and member.state.current_hp > 0]


def select_nearest_target(attacker: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    """Arena tactic: engage the nearest living enemy; encounter order breaks distance ties."""
    try:
        opponents = living_opponents(attacker, setup)
        if not opponents:
            return None
        return min(opponents, key=lambda target: combatant_distance(attacker, target))
    except Exception as exc:
        logger.exception("Target selection failed for %s.", attacker.combatant_id)
        raise RuntimeError("Encounter target could not be selected.") from exc
