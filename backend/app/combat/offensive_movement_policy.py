from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.offensive_ranges import offensive_ranges_for_target
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import OffensiveMovementIntent
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def choose_offensive_movement_intent(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> OffensiveMovementIntent | None:
    """Return the smallest legal closing requirement only when no offense is legal now."""
    try:
        if not is_available(attacker.state, "action"):
            return None
        candidates: list[tuple[int, int, str, str, int]] = []
        offense_legal_now = False
        for target in living_opponents(attacker, setup):
            distance = combatant_distance(attacker, target)
            for family, desired_distance in offensive_ranges_for_target(attacker, target, turn_key):
                if distance <= desired_distance:
                    offense_legal_now = True
                    continue
                needed = distance - desired_distance
                candidates.append((needed, distance, target.combatant_id, family, desired_distance))
        if offense_legal_now or not candidates:
            return None
        _, _, target_id, family, desired_distance = min(candidates)
        return OffensiveMovementIntent(
            target_id=target_id,
            desired_distance_ft=desired_distance,
            family=family,
        )
    except Exception as exc:
        logger.exception("Failed offensive movement intent for %s.", attacker.combatant_id)
        raise RuntimeError("Offensive movement intent could not be evaluated.") from exc


def move_to_enable_offense(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Move only when movement can pursue a currently unavailable supported offensive family."""
    try:
        if setup.map_definition is None:
            return [], sequence
        intent = choose_offensive_movement_intent(attacker, setup, turn_key)
        if intent is None:
            return [], sequence
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        target = members.get(intent.target_id)
        if target is None:
            raise ValueError(f"Offensive movement target {intent.target_id!r} is missing.")
        events, sequence, _ = move_toward_with_reactions(
            sequence,
            round_number,
            attacker,
            target,
            setup,
            intent.desired_distance_ft,
            dice,
            turn_key=turn_key,
        )
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed movement-to-offense execution for %s.", attacker.combatant_id)
        raise RuntimeError("Offensive movement could not be resolved.") from exc
