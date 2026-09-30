from pydantic import ValidationError

from app.domain.grid import GridPosition
from app.domain.persistent_barriers import (
    GridBarrierEdge,
    PersistentBarrierAction,
    PersistentBarrierSectionState,
    PersistentBarrierState,
)


def test_barrier_edge_requires_one_orthogonal_grid_transition() -> None:
    edge = GridBarrierEdge(
        first=GridPosition(x=4, y=5),
        second=GridPosition(x=5, y=5),
    )
    assert edge.canonical_key() == ((4, 5), (5, 5))

    reverse = GridBarrierEdge(
        first=GridPosition(x=5, y=5),
        second=GridPosition(x=4, y=5),
    )
    assert reverse.canonical_key() == edge.canonical_key()

    try:
        GridBarrierEdge(
            first=GridPosition(x=4, y=5),
            second=GridPosition(x=5, y=6),
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Diagonal barrier edges must fail closed.")


def test_persistent_barrier_separates_source_parameters_from_runtime_state() -> None:
    action = PersistentBarrierAction(
        id="test-stone-wall",
        name="Test Stone Wall",
        level=5,
        cast_range_ft=120,
        concentration=True,
        duration_rounds=100,
        max_sections=10,
        section_length_ft=10,
        section_height_ft=10,
        section_thickness_inches=6,
        armor_class=15,
        hit_points_per_section=180,
        damage_immunities=["poison", "psychic"],
        material="stone",
    )
    edge = GridBarrierEdge(
        first=GridPosition(x=6, y=6),
        second=GridPosition(x=7, y=6),
    )
    section = PersistentBarrierSectionState(
        section_id="panel-1",
        edges=[edge],
        current_hp=action.hit_points_per_section,
        armor_class=action.armor_class,
        damage_immunities=action.damage_immunities,
    )
    state = PersistentBarrierState(
        barrier_id="caster:test-stone-wall:1",
        source_id="caster",
        source_side="heroes",
        action_id=action.id,
        action_name=action.name,
        concentration=action.concentration,
        applied_round=1,
        expires_round=101,
        sections=[section],
    )

    assert action.hit_points_per_section == 180
    assert state.sections[0].current_hp == 180
    assert state.sections[0].destroyed is False
    assert state.sections[0].edges[0].canonical_key() == ((6, 6), (7, 6))
