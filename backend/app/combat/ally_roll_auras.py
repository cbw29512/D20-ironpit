from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _allies(member: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return setup.heroes if member.side == "heroes" else setup.monsters


def ally_roll_aura_advantage_sources(
    member: EncounterCombatant,
    setup: EncounterSetup,
    *,
    roll_kind: str,
) -> int:
    """Count active allied auras that grant Advantage to this member's requested roll kind."""
    if roll_kind not in {"attack", "saving_throw"}:
        raise ValueError(f"Unsupported ally roll aura kind {roll_kind!r}.")
    total = 0
    for source in _allies(member, setup):
        if not source.state.is_alive or source.state.is_dead:
            continue
        for aura in source.state.template.ally_roll_auras:
            grants = aura.attack_advantage if roll_kind == "attack" else aura.saving_throw_advantage
            if not grants:
                continue
            if aura.suppressed_if_incapacitated and is_incapacitated(source.state):
                continue
            if combatant_distance(source, member) <= aura.radius_ft:
                total += 1
    return total
