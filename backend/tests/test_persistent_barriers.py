from pydantic import ValidationError

from app.combat.grid_pathing import plan_movement_toward
from app.combat.grid_pathing_support import movement_step_cost_ft
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.persistent_barriers import (
    GridBarrierEdge,
    PersistentBarrierAction,
    PersistentBarrierSectionState,
    PersistentBarrierState,
)

MAP = BattleMapDefinition(id="barrier-test", width_squares=8, height_squares=8)


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(
        update={"id": combatant_id, "name": combatant_id},
    )
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=state,
    )


def _barrier(*edges: tuple[tuple[int, int], tuple[int, int]]) -> PersistentBarrierState:
    return PersistentBarrierState(
        barrier_id="test-barrier",
        source_id="caster",
        source_side="heroes",
        action_id="test-stone-wall",
        action_name="Test Stone Wall",
        concentration=True,
        applied_round=1,
        expires_round=101,
        sections=[
            PersistentBarrierSectionState(
                section_id=f"panel-{index}",
                edges=[
                    GridBarrierEdge(
                        first=GridPosition(x=first[0], y=first[1]),
                        second=GridPosition(x=second[0], y=second[1]),
                    ),
                ],
                current_hp=180,
                armor_class=15,
                damage_immunities=["poison", "psychic"],
            )
            for index, (first, second) in enumerate(edges, start=1)
        ],
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
    state = _barrier(((6, 6), (7, 6)))

    assert action.hit_points_per_section == 180
    assert state.sections[0].current_hp == 180
    assert state.sections[0].destroyed is False


def test_live_barrier_blocks_direct_transition_and_pathfinder_routes_around_it() -> None:
    mover = _member("mover", "heroes", 0, 0)
    target = _member("target", "monsters", 3, 0)
    barrier = _barrier(((0, 0), (1, 0)))

    assert movement_step_cost_ft(
        MAP,
        mover,
        GridPosition(x=1, y=0),
        [mover, target],
        origin=GridPosition(x=0, y=0),
        barriers=[barrier],
    ) is None

    plan = plan_movement_toward(
        MAP,
        mover,
        target,
        [mover, target],
        5,
        30,
        [barrier],
    )
    assert plan.path
    assert (plan.path[0].x, plan.path[0].y) != (1, 0)
    assert plan.goal_reachable is True


def test_destroyed_barrier_section_reopens_its_transition() -> None:
    mover = _member("mover", "heroes", 0, 0)
    target = _member("target", "monsters", 3, 0)
    barrier = _barrier(((0, 0), (1, 0)))
    barrier.sections[0].current_hp = 0
    barrier.sections[0].destroyed = True

    assert movement_step_cost_ft(
        MAP,
        mover,
        GridPosition(x=1, y=0),
        [mover, target],
        origin=GridPosition(x=0, y=0),
        barriers=[barrier],
    ) == 5
