from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.domain.auras import RollAdvantageAura
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _source_active(source: EncounterCombatant, aura: RollAdvantageAura) -> bool:
    state = source.state
    if state.is_dead or not state.is_alive:
        return False
    return not (aura.disabled_while_incapacitated and is_incapacitated(state))


def _eligible(source: EncounterCombatant, subject: EncounterCombatant, aura: RollAdvantageAura) -> bool:
    if source.combatant_id == subject.combatant_id:
        return aura.target_scope in {"self", "self-and-allies"}
    return source.side == subject.side and aura.target_scope in {"allies", "self-and-allies"}


def _advantage_sources(subject: EncounterCombatant, setup: EncounterSetup | None, *, attack: bool) -> int:
    if setup is None:
        return 0
    total = 0
    for source in [*setup.heroes, *setup.monsters]:
        for aura in source.state.template.roll_advantage_auras:
            grants = aura.attack_roll_advantage if attack else aura.saving_throw_advantage
            if not grants or not _source_active(source, aura) or not _eligible(source, subject, aura):
                continue
            if combatant_distance(source, subject) <= aura.radius_ft:
                total += 1
    return total


def attack_advantage_sources(subject: EncounterCombatant, setup: EncounterSetup | None) -> int:
    return _advantage_sources(subject, setup, attack=True)


def saving_throw_advantage_sources(subject: EncounterCombatant, setup: EncounterSetup | None) -> int:
    return _advantage_sources(subject, setup, attack=False)
