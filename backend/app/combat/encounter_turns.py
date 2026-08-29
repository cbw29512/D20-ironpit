from __future__ import annotations

import logging

from app.combat.encounter_movement import move_toward_combatant, take_encounter_dash
from app.combat.encounter_targeting import combatant_distance
from app.combat.policy import preferred_approach_distance, select_weapon_attack
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)


def prepare_encounter_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
) -> tuple[WeaponAttack | None, list[BattleEvent], int]:
    """Close toward preferred range, then attack or Dash if the target remains unreachable."""
    try:
        events: list[BattleEvent] = []
        desired = preferred_approach_distance(attacker.state)
        movement = move_toward_combatant(sequence, round_number, attacker, target, desired)
        if movement is not None:
            events.append(movement)
            sequence += 1

        distance = combatant_distance(attacker, target)
        attack = select_weapon_attack(attacker.state, distance)
        if attack is not None and attacker.state.action_available:
            return attack, events, sequence

        if attacker.state.action_available:
            events.append(take_encounter_dash(sequence, round_number, attacker, target))
            sequence += 1
            movement = move_toward_combatant(sequence, round_number, attacker, target, desired)
            if movement is not None:
                events.append(movement)
                sequence += 1

        if not attacker.state.action_available:
            return None, events, sequence
        attack = select_weapon_attack(attacker.state, combatant_distance(attacker, target))
        return attack, events, sequence
    except Exception as exc:
        logger.exception("Encounter turn preparation failed for %s.", attacker.combatant_id)
        raise RuntimeError("Encounter turn could not be prepared.") from exc
