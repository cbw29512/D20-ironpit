from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.tactical_actions import choose_offensive_dash_grant, use_offensive_dash
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.formation_rows import member_is_backline
from app.combat.grid_pathing import plan_movement_toward
from app.combat.modifier_stack import effective_speed
from app.combat.offensive_ranges import offensive_ranges_for_target, tightest_usable_melee_reach_ft
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
    """Return the cheapest useful movement intent toward a supported offensive position."""
    try:
        if not is_available(attacker.state, "action") or setup.map_definition is None:
            return None
        if attacker.state.position is None:
            raise ValueError("Grid offensive movement requires an authoritative attacker position.")
        members = [*setup.heroes, *setup.monsters]
        melee_reach: list[tuple[int, int, str, str, int]] = []
        melee_progress: list[tuple[int, int, str, str, int]] = []
        ranged_progress: list[tuple[int, int, str, str, int]] = []
        melee_legal_now = False
        other_legal_now = False
        for target in living_opponents(attacker, setup):
            if target.state.position is None:
                raise ValueError("Grid offensive movement requires authoritative target positions.")
            distance = combatant_distance(attacker, target)
            preferred_melee = tightest_usable_melee_reach_ft(attacker, target)
            for family, desired_distance in offensive_ranges_for_target(attacker, target, turn_key):
                goal = preferred_melee if family == "melee" and preferred_melee is not None else desired_distance
                if distance <= goal:
                    if family == "melee":
                        melee_legal_now = True
                    else:
                        other_legal_now = True
                    continue
                plan = plan_movement_toward(
                    setup.map_definition,
                    attacker,
                    target,
                    members,
                    goal,
                    attacker.state.movement_remaining_ft,
                    setup.persistent_barriers,
                    setup.temporary_terrain_zones,
                )
                if not plan.path:
                    continue
                row = (
                    plan.movement_cost_ft,
                    distance,
                    target.combatant_id,
                    family,
                    goal,
                )
                if family == "melee" and plan.final_distance_ft <= goal:
                    melee_reach.append(row)
                elif family == "melee" and plan.final_distance_ft < distance:
                    melee_progress.append(row)
                elif plan.final_distance_ft < distance:
                    ranged_progress.append(row)
        if melee_legal_now:
            return None
        if member_is_backline(attacker):
            chosen = melee_reach or ([] if other_legal_now else ranged_progress or melee_progress)
        else:
            chosen = melee_reach or melee_progress
        if not chosen:
            return None
        _, _, target_id, family, desired_distance = min(chosen)
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


def melee_can_be_enabled_this_turn(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
) -> bool:
    """True when a melee attack can land now or after this turn's legal approach."""
    try:
        for target in living_opponents(attacker, setup):
            for family, desired_distance in offensive_ranges_for_target(attacker, target, turn_key):
                if family == "melee" and combatant_distance(attacker, target) <= desired_distance:
                    return True
        if setup.map_definition is None or attacker.state.position is None:
            return False
        budget = attacker.state.movement_remaining_ft
        if choose_offensive_dash_grant(attacker, setup, turn_key) is not None:
            budget += effective_speed(attacker.state)
        members = [*setup.heroes, *setup.monsters]
        for target in living_opponents(attacker, setup):
            if target.state.position is None:
                raise ValueError("Grid offensive movement requires authoritative target positions.")
            for family, desired_distance in offensive_ranges_for_target(attacker, target, turn_key):
                if family != "melee":
                    continue
                plan = plan_movement_toward(
                    setup.map_definition,
                    attacker,
                    target,
                    members,
                    desired_distance,
                    budget,
                    setup.persistent_barriers,
                    setup.temporary_terrain_zones,
                )
                if plan.goal_reachable and plan.path and plan.final_distance_ft <= desired_distance:
                    return True
        return False
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed melee-enable probe for %s.", attacker.combatant_id)
        raise RuntimeError("Melee enablement could not be evaluated.") from exc


def move_to_enable_offense(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Advance only along a route that can eventually enable supported offense."""
    try:
        if setup.map_definition is None:
            return [], sequence
        events: list[BattleEvent] = []
        dash = use_offensive_dash(sequence, round_number, attacker, setup, turn_key)
        if dash is not None:
            events.append(dash); sequence += 1
        intent = choose_offensive_movement_intent(attacker, setup, turn_key)
        if intent is None:
            return events, sequence
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        target = members.get(intent.target_id)
        if target is None:
            raise ValueError(f"Offensive movement target {intent.target_id!r} is missing.")
        moved, sequence, _ = move_toward_with_reactions(
            sequence, round_number, attacker, target, setup, intent.desired_distance_ft, dice, turn_key=turn_key,
        )
        events.extend(moved)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed movement-to-offense execution for %s.", attacker.combatant_id)
        raise RuntimeError("Offensive movement could not be resolved.") from exc
