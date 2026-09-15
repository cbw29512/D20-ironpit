from types import SimpleNamespace

from app.combat import area_movement_choice
from app.domain.grid import BattleMapDefinition, GridDestinationPlan, GridPosition
from app.domain.targeting import AreaTargeting


def _member(member_id: str, side: str, x: int, y: int):
    return SimpleNamespace(
        combatant_id=member_id,
        side=side,
        state=SimpleNamespace(
            position=GridPosition(x=x, y=y),
            is_alive=True,
            is_dead=False,
            current_hp=10,
            template=SimpleNamespace(size="medium"),
        ),
    )


def test_best_area_destination_scores_hypothetical_reachable_square(monkeypatch) -> None:
    actor = _member("actor", "heroes", 0, 0)
    target = _member("target", "monsters", 2, 0)
    setup = SimpleNamespace(
        heroes=[actor],
        monsters=[target],
        map_definition=BattleMapDefinition(id="test", width_squares=6, height_squares=4),
    )
    action = SimpleNamespace(
        id="emanation",
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=5),
        range_ft=0,
    )
    reachable = [
        GridDestinationPlan(destination=GridPosition(x=0, y=0), path=[], movement_cost_ft=0),
        GridDestinationPlan(
            destination=GridPosition(x=1, y=0),
            path=[GridPosition(x=1, y=0)],
            movement_cost_ft=5,
        ),
    ]
    monkeypatch.setattr(area_movement_choice, "save_action_expected_damage", lambda *_: 10.0)

    choice = area_movement_choice.best_area_destination(actor, setup, action, reachable)

    assert choice is not None
    assert choice.destination_plan.destination == GridPosition(x=1, y=0)
    assert choice.placement.target_ids == ("target",)
    assert choice.expected_value == 10.0
    assert actor.state.position == GridPosition(x=0, y=0)
