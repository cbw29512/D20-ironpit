from __future__ import annotations

from app.combat.grid_passage import can_pass_through, creature_space_is_difficult
from app.combat.grid_pathing import movement_step_cost_ft, plan_movement_toward
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.size import CreatureSize

MAP = BattleMapDefinition(id="movement-test", width_squares=8, height_squares=8)


def _member(
    combatant_id: str,
    side: str,
    x: int,
    y: int,
    *,
    size: CreatureSize = CreatureSize.MEDIUM,
    incapacitated: bool = False,
) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(
        update={"id": combatant_id, "name": combatant_id, "size": size},
    )
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    state.is_unconscious = incapacitated
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)


def test_creature_space_passage_uses_2024_side_condition_and_size_rules() -> None:
    mover = _member("mover", "heroes", 0, 0)
    ally = _member("ally", "heroes", 1, 1)
    hostile = _member("hostile", "monsters", 1, 1)
    incapacitated = _member("incapacitated", "monsters", 1, 1, incapacitated=True)
    tiny = _member("tiny", "monsters", 1, 1, size=CreatureSize.TINY)
    huge = _member("huge", "monsters", 1, 1, size=CreatureSize.HUGE)

    assert can_pass_through(mover, ally)
    assert not creature_space_is_difficult(mover, ally)
    assert not can_pass_through(mover, hostile)
    assert can_pass_through(mover, incapacitated)
    assert creature_space_is_difficult(mover, incapacitated)
    assert can_pass_through(mover, tiny)
    assert not creature_space_is_difficult(mover, tiny)
    assert can_pass_through(mover, huge)
    assert creature_space_is_difficult(mover, huge)


def test_step_cost_distinguishes_open_ally_difficult_and_blocked_spaces() -> None:
    mover = _member("mover", "heroes", 0, 0)
    destination = GridPosition(x=1, y=1)

    assert movement_step_cost_ft(MAP, mover, destination, [mover]) == 5

    ally = _member("ally", "heroes", 1, 1)
    assert movement_step_cost_ft(MAP, mover, destination, [mover, ally]) == 5

    hostile = _member("hostile", "monsters", 1, 1)
    assert movement_step_cost_ft(MAP, mover, destination, [mover, hostile]) is None

    incapacitated = _member("incapacitated", "monsters", 1, 1, incapacitated=True)
    assert movement_step_cost_ft(MAP, mover, destination, [mover, incapacitated]) == 10


def test_plan_toward_uses_diagonal_grid_steps_and_stops_at_melee_reach() -> None:
    mover = _member("mover", "heroes", 0, 0)
    target = _member("target", "monsters", 3, 3)

    plan = plan_movement_toward(MAP, mover, target, [mover, target], 5, 30)

    assert [(step.x, step.y) for step in plan.path] == [(1, 1), (2, 2)]
    assert plan.movement_cost_ft == 10
    assert plan.final_distance_ft == 5
    assert plan.goal_reachable is True


def test_plan_toward_never_ends_in_an_occupied_space() -> None:
    mover = _member("mover", "heroes", 0, 0)
    ally = _member("ally", "heroes", 1, 1)
    target = _member("target", "monsters", 3, 3)

    plan = plan_movement_toward(MAP, mover, target, [mover, ally, target], 5, 30)

    assert plan.path
    assert (plan.path[-1].x, plan.path[-1].y) != (1, 1)
    assert plan.final_distance_ft == 5
    assert plan.goal_reachable is True


def test_full_route_search_moves_sideways_when_short_budget_cannot_immediately_close() -> None:
    mover = _member("mover", "heroes", 0, 0)
    target = _member("target", "monsters", 4, 0)
    blockers = [
        _member("blocker-a", "monsters", 1, 0),
        _member("blocker-b", "monsters", 1, 1),
    ]

    plan = plan_movement_toward(MAP, mover, target, [mover, target, *blockers], 5, 5)

    assert [(step.x, step.y) for step in plan.path] == [(0, 1)]
    assert plan.movement_cost_ft == 5
    assert plan.final_distance_ft == 20
    assert plan.goal_reachable is True


def test_diagonal_path_cannot_squeeze_between_two_blocked_orthogonal_spaces() -> None:
    mover = _member("mover", "heroes", 0, 0)
    target = _member("target", "monsters", 2, 2)
    blockers = [
        _member("blocker-east", "monsters", 1, 0),
        _member("blocker-south", "monsters", 0, 1),
    ]

    plan = plan_movement_toward(MAP, mover, target, [mover, target, *blockers], 5, 30)

    assert plan.path == []
    assert plan.movement_cost_ft == 0
    assert plan.final_distance_ft == 10
    assert plan.goal_reachable is False
