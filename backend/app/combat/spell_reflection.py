from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup


def reflection_target(
    reflector: EncounterCombatant,
    caster: EncounterCombatant,
    setup: EncounterSetup,
) -> EncounterCombatant | None:
    """Choose the deterministic Iron Pit target for a reflected single-target spell."""
    profile = reflector.state.template.spell_reflection_reaction
    if profile is None or not is_available(reflector.state, "reaction"):
        return None
    members = [*setup.heroes, *setup.monsters]
    legal = [
        member for member in members
        if member is not reflector and member.state.is_alive and not member.state.is_dead
        and combatant_distance(reflector, member) <= profile.range_ft
    ]
    if caster in legal:
        return caster
    legal.sort(key=lambda member: (combatant_distance(reflector, member), member.combatant_id))
    return legal[0] if legal else None


def spend_spell_reflection(reflector: EncounterCombatant) -> None:
    if not is_available(reflector.state, "reaction"):
        raise ValueError("Spell Reflection reaction is unavailable.")
    spend(reflector.state, "reaction")
