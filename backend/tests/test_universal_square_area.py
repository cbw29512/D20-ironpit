"""Reusable 2x2 landing geometry: immutable source coordinates and exact target cells."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.area_shapes import square_contains, cell_center_ft
from app.combat.area_targeting import legal_area_placements
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting


def _member(ident, side, x, y):
    member = EncounterCombatant(
        combatant_id=ident, side=side, position_ft=x * 5,
        state=build_combatant_state(build_demo_fighter()),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def test_square_hits_exactly_four_cells_not_circular_area() -> None:
    origin = cell_center_ft(5, 4)
    for x, y in [(5, 4), (6, 4), (5, 5), (6, 5)]:
        assert square_contains(origin, cell_center_ft(x, y), 10)
    for x, y in [(4, 4), (7, 4), (5, 6), (6, 3)]:
        assert not square_contains(origin, cell_center_ft(x, y), 10)


def test_square_keeps_distinct_origins_when_target_set_matches() -> None:
    actor = _member("actor", "monsters", 1, 4)
    foe = _member("foe", "heroes", 5, 4)
    setup = EncounterSetup(
        heroes=[foe], monsters=[actor], ruleset="2014",
        hero_total_levels=1, monster_total_cr="1",
        map_definition=BattleMapDefinition(id="square-test", width_squares=10, height_squares=10),
    )
    area = AreaTargeting(shape="square", origin="point", length_ft=10)
    places = legal_area_placements(actor, setup, area, 30)
    matched = [p for p in places if "foe" in p.target_ids]
    # Two different nearby landing regions can include the same target;
    # movement eligibility must be able to select between those origins.
    assert len({p.origin for p in matched}) >= 2
    assert not any("actor" in p.target_ids for p in places)


def test_invalid_square_shape_rejected() -> None:
    with pytest.raises(ValidationError, match="Square area"):
        AreaTargeting(shape="square", origin="self", length_ft=10)
    with pytest.raises(ValidationError):
        AreaTargeting(shape="square", origin="point", length_ft=7)
