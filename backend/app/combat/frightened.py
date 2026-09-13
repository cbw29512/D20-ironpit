from __future__ import annotations

from app.combat.condition_rules import has_condition
from app.combat.visibility import has_line_of_sight
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import CombatantState

FRIGHTENED_EFFECT_ID = "frightened"


def fear_source_ids(state: CombatantState) -> tuple[str, ...]:
    if not has_condition(state, FRIGHTENED_EFFECT_ID):
        return ()
    source_ids = tuple(dict.fromkeys(
        effect.source_id for effect in state.timed_effects
        if effect.effect_id == FRIGHTENED_EFFECT_ID
    ))
    if not source_ids:
        raise ValueError("Active Frightened condition lacks source-bound lifecycle state.")
    return source_ids


def _members(setup: EncounterSetup) -> dict[str, EncounterCombatant]:
    return {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}


def fear_sources(state: CombatantState, setup: EncounterSetup) -> tuple[EncounterCombatant, ...]:
    members = _members(setup)
    resolved: list[EncounterCombatant] = []
    for source_id in fear_source_ids(state):
        source = members.get(source_id)
        if source is None:
            raise ValueError(f"Frightened source {source_id!r} is missing from the encounter.")
        resolved.append(source)
    return tuple(resolved)


def frightened_d20_disadvantage(state: CombatantState, setup: EncounterSetup) -> int:
    """Return one Disadvantage source when any fear source is currently visible."""
    return int(any(has_line_of_sight(state, source.state) for source in fear_sources(state, setup)))
