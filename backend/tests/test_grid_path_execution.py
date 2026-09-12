from types import SimpleNamespace

from app.combat import grid_path_execution
from app.domain.grid import BattleMapDefinition, GridPosition


def test_execute_grid_path_moves_exact_targetless_route(monkeypatch) -> None:
    mover = SimpleNamespace(
        combatant_id="mover",
        side="heroes",
        state=SimpleNamespace(
            position=GridPosition(x=0, y=0),
            movement_remaining_ft=10,
            active_effect_ids=[],
            is_dead=False,
            is_unconscious=False,
            template=SimpleNamespace(name="Mover", size="medium"),
        ),
    )
    setup = SimpleNamespace(
        heroes=[mover],
        monsters=[],
        map_definition=BattleMapDefinition(id="test", width_squares=4, height_squares=4),
    )
    monkeypatch.setattr(grid_path_execution, "approaches_fear_source", lambda *_: False)
    monkeypatch.setattr(grid_path_execution, "movement_step_cost_ft", lambda *_: 5)
    monkeypatch.setattr(grid_path_execution, "speed_is_zero", lambda *_: False)

    events, sequence, movement = grid_path_execution.execute_grid_path(
        1,
        1,
        mover,
        setup,
        [GridPosition(x=1, y=0), GridPosition(x=2, y=0)],
        SimpleNamespace(),
    )

    assert sequence == 3
    assert len(events) == 2
    assert movement is events[-1]
    assert mover.state.position == GridPosition(x=2, y=0)
    assert mover.state.movement_remaining_ft == 0
    assert all(event.target_id is None for event in events)
