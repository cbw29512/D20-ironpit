from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition, is_incapacitated
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def combatant_distance(attacker: EncounterCombatant, target: EncounterCombatant) -> int:
    return abs(attacker.position_ft - target.position_ft)


def _opponents(attacker: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return setup.monsters if attacker.side == "heroes" else setup.heroes


def close_ranged_threat_exists(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    """Pit visibility is unobstructed; only a non-Incapacitated enemy within 5 ft. threatens a ranged attack."""
    return any(
        member.state.is_alive
        and not member.state.is_dead
        and member.state.current_hp > 0
        and not is_incapacitated(member.state)
        and combatant_distance(attacker, member) <= 5
        for member in _opponents(attacker, setup)
    )


def _target_priority(member: EncounterCombatant) -> int | None:
    """Iron Pit policy: active enemies first, Petrified statues second, downed characters last."""
    state = member.state
    if not state.is_alive or state.is_dead:
        return None
    if state.current_hp > 0:
        return 1 if has_condition(state, "petrified") else 0
    if state.template.kind == "character" and state.current_hp == 0:
        return 2
    return None


def living_opponents(attacker: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    """Return only the highest-priority eligible target class under deterministic Pit policy."""
    candidates = [member for member in _opponents(attacker, setup) if _target_priority(member) is not None]
    if not candidates:
        return []
    priority = min(_target_priority(member) for member in candidates)
    return [member for member in candidates if _target_priority(member) == priority]


def select_nearest_target(attacker: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    """Within the current target class, finish a held target, fight a grappler, then engage nearest."""
    try:
        opponents = living_opponents(attacker, setup)
        if not opponents:
            return None
        held = [
            target for target in opponents
            if any(source.source_id == attacker.combatant_id for source in target.state.grapple_sources)
        ]
        if held:
            return min(held, key=lambda target: combatant_distance(attacker, target))
        grappler_ids = {source.source_id for source in attacker.state.grapple_sources}
        grapplers = [target for target in opponents if target.combatant_id in grappler_ids]
        choices = grapplers or opponents
        return min(choices, key=lambda target: combatant_distance(attacker, target))
    except Exception as exc:
        logger.exception("Target selection failed for %s.", attacker.combatant_id)
        raise RuntimeError("Encounter target could not be selected.") from exc
