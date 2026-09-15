from types import SimpleNamespace

from app.combat.area_targeting import legal_area_placements
from app.domain.grid import BattleMapDefinition, GridPosition
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


def test_area_targeting_can_score_hypothetical_actor_position_without_mutation() -> None:
    actor = _member("actor", "heroes", 0, 0)
    target = _member("target", "monsters", 2, 0)
    setup = SimpleNamespace(
        heroes=[actor],
        monsters=[target],
        map_definition=BattleMapDefinition(id="test", width_squares=6, height_squares=4),
    )
    area = AreaTargeting(shape="emanation", origin="self", radius_ft=5)

    assert legal_area_placements(actor, setup, area, 0) == []

    placements = legal_area_placements(
        actor,
        setup,
        area,
        0,
        actor_position=GridPosition(x=1, y=0),
    )

    assert placements
    assert placements[0].target_ids == ("target",)
    assert actor.state.position == GridPosition(x=0, y=0)
