from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.grid_pathing import plan_movement_toward
from app.combat.offensive_ranges import ranked_offensive_range_profiles_for_target
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
    """Move toward the highest-priority, highest-value offense when movement improves its use."""
    try:
        if not is_available(attacker.state, "action") or setup.map_definition is None:
            return None
        if attacker.state.position is None:
            raise ValueError("Grid offensive movement requires an authoritative attacker position.")
        members = [*setup.heroes, *setup.monsters]
        candidates: list[tuple[int, int, float, int, int, str, str, int]] = []
        for target in living_opponents(attacker, setup):
            if target.state.position is None:
                raise ValueError("Grid offensive movement requires authoritative target positions.")
            distance = combatant_distance(attacker, target)
            profiles = ranked_offensive_range_profiles_for_target(attacker, target, turn_key, setup)
            for profile in profiles:
                base = (
                    profile.priority,
                    profile.execution_rank,
                    -profile.expected_value,
                )
                if distance <= profile.preferred_range_ft:
                    candidates.append((
                        *base,
                        0,
                        distance,
                        target.combatant_id,
                        profile.family,
                        profile.preferred_range_ft,
                    ))
                    continue
                plan = plan_movement_toward(
                    setup.map_definition,
                    attacker,
                    target,
                    members,
                    profile.preferred_range_ft,
                    attacker.state.movement_remaining_ft,
                )
                if plan.goal_reachable and plan.path and plan.final_distance_ft < distance:
                    candidates.append((
                        *base,
                        plan.movement_cost_ft,
                        distance,
                        target.combatant_id,
                        profile.family,
                        profile.preferred_range_ft,
                    ))
                    continue
                if distance <= profile.max_range_ft:
                    candidates.append((
                        *base,
                        0,
                        distance,
                        target.combatant_id,
                        profile.family,
                        profile.preferred_range_ft,
                    ))
        if not candidates:
            return None
        _, _, _, movement_cost, _, target_id, family, desired_distance = min(candidates)
        if movement_cost == 0:
            return None
        return OffensiveMovementIntent(
            target_id=target_id,
            desired_distance_ft=desired_distance,
            family=family,
        )
    except ValueError:
        raise
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
    """Advance along a legal route that enables or improves the preferred offense."""
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
