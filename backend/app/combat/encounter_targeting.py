from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def combatant_distance(attacker: EncounterCombatant, target: EncounterCombatant) -> int:
    return abs(attacker.position_ft - target.position_ft)


def _opponents(attacker: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return setup.monsters if attacker.side == "heroes" else setup.heroes


def living_opponents(attacker: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    """Prefer standing enemies; if none remain, return living downed characters for deathmatch resolution."""
    candidates = _opponents(attacker, setup)
    standing = [
        member for member in candidates
        if member.state.is_alive and not member.state.is_dead and member.state.current_hp > 0
    ]
    if standing:
        return standing
    return [
        member for member in candidates
        if (
            member.state.template.kind == "character"
            and member.state.is_alive
            and not member.state.is_dead
            and member.state.current_hp == 0
        )
    ]


def select_nearest_target(attacker: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    """Arena tactic: engage the nearest eligible enemy; encounter order breaks distance ties."""
    try:
        opponents = living_opponents(attacker, setup)
        if not opponents:
            return None
        return min(opponents, key=lambda target: combatant_distance(attacker, target))
    except Exception as exc:
        logger.exception("Target selection failed for %s.", attacker.combatant_id)
        raise RuntimeError("Encounter target could not be selected.") from exc
