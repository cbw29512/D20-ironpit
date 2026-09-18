from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.cunning_action import use_dash
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.grid_pathing import plan_movement_toward
from app.combat.modifier_stack import effective_speed
from app.combat.offensive_ranges import offensive_ranges_for_target
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import OffensiveMovementIntent
from app.domain.models import BattleEvent
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _movement_budget(attacker: EncounterCombatant) -> tuple[int, bool]:
    try:
        base = attacker.state.movement_remaining_ft
        aggressive = CombatTrait.AGGRESSIVE in attacker.state.template.combat_traits
        can_bonus_move = aggressive and is_available(attacker.state, "bonus_action")
        return base + (effective_speed(attacker.state) if can_bonus_move else 0), can_bonus_move
    except Exception as exc:
        logger.exception("Failed bonus-action movement budget for %s.", attacker.combatant_id)
        raise RuntimeError("Offensive movement budget could not be evaluated.") from exc


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
        budget, can_bonus_move = _movement_budget(attacker)
        base_budget = attacker.state.movement_remaining_ft
        candidates: list[tuple[int, int, str, str, int, bool]] = []
        offense_legal_now = False
        for target in living_opponents(attacker, setup):
            if target.state.position is None:
                raise ValueError("Grid offensive movement requires authoritative target positions.")
            distance = combatant_distance(attacker, target)
            for family, desired_distance in offensive_ranges_for_target(attacker, target, turn_key):
                if distance <= desired_distance:
                    offense_legal_now = True
                    continue
                plan = plan_movement_toward(
                    setup.map_definition,
                    attacker,
                    target,
                    members,
                    desired_distance,
                    budget,
                )
                if not plan.goal_reachable or not plan.path or plan.final_distance_ft >= distance:
                    continue
                candidates.append((
                    plan.movement_cost_ft,
                    distance,
                    target.combatant_id,
                    family,
                    desired_distance,
                    can_bonus_move and plan.movement_cost_ft > base_budget,
                ))
        if offense_legal_now or not candidates:
            return None
        _, _, target_id, family, desired_distance, uses_bonus = min(candidates)
        return OffensiveMovementIntent(
            target_id=target_id,
            desired_distance_ft=desired_distance,
            family=family,
            uses_bonus_action_movement=uses_bonus,
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
    """Advance only along a route that can eventually enable supported offense."""
    try:
        if setup.map_definition is None:
            return [], sequence
        events: list[BattleEvent] = []
        dash = use_dash(sequence, round_number, attacker, setup, turn_key)
        if dash is not None:
            events.append(dash)
            sequence += 1
        intent = choose_offensive_movement_intent(attacker, setup, turn_key)
        if intent is None:
            return events, sequence
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        target = members.get(intent.target_id)
        if target is None:
            raise ValueError(f"Offensive movement target {intent.target_id!r} is missing.")
        if intent.uses_bonus_action_movement:
            speed = effective_speed(attacker.state)
            spend(attacker.state, "bonus_action")
            attacker.state.movement_remaining_ft += speed
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=attacker.combatant_id,
                actor_name=attacker.state.template.name,
                feature_id="aggressive",
                movement_ft=speed,
                animation="advance",
                description=f"{attacker.state.template.name} uses Aggressive to surge toward an enemy.",
            ))
            sequence += 1
        moved, sequence, _ = move_toward_with_reactions(
            sequence,
            round_number,
            attacker,
            target,
            setup,
            intent.desired_distance_ft,
            dice,
            turn_key=turn_key,
        )
        events.extend(moved)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed movement-to-offense execution for %s.", attacker.combatant_id)
        raise RuntimeError("Offensive movement could not be resolved.") from exc
