from types import SimpleNamespace

from app.combat import grid_reachable
from app.domain.grid import BattleMapDefinition, GridPosition


def test_reachable_grid_destinations_include_start_and_budget_paths(monkeypatch) -> None:
    mover = SimpleNamespace(
        combatant_id="mover",
        state=SimpleNamespace(position=GridPosition(x=0, y=0)),
    )
    map_definition = BattleMapDefinition(
        id="test-map",
        width_squares=4,
        height_squares=4,
    )

    monkeypatch.setattr(grid_reachable, "overlapping_occupants", lambda *_: [])
    monkeypatch.setattr(
        grid_reachable,
        "movement_step_cost_ft",
        lambda _map, _mover, destination, _members: (
            5 if 0 <= destination.x < 4 and 0 <= destination.y < 4 else None
        ),
    )

    plans = grid_reachable.reachable_grid_destinations(
        map_definition,
        mover,
        [mover],
        10,
    )

    by_destination = {
        (plan.destination.x, plan.destination.y): plan
        for plan in plans
    }
    assert by_destination[(0, 0)].movement_cost_ft == 0
    assert by_destination[(1, 0)].movement_cost_ft == 5
    assert by_destination[(2, 0)].movement_cost_ft == 10
    assert [(step.x, step.y) for step in by_destination[(2, 0)].path] == [(1, 0), (2, 0)]
    assert (3, 0) not in by_destination
