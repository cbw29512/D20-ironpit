from app.combat.barrier_line_of_effect import clear_line_between_members
from app.combat.grid_barriers import barrier_blocks_transition
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_barriers import (
    GridBarrierEdge,
    PersistentBarrierSectionState,
    PersistentBarrierState,
)


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(update={"id": combatant_id, "name": combatant_id})
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _wall() -> PersistentBarrierState:
    return PersistentBarrierState(
        barrier_id="wall",
        source_id="source",
        source_side="heroes",
        action_id="test-wall",
        action_name="Test Wall",
        applied_round=1,
        expires_round=10,
        sections=[
            PersistentBarrierSectionState(
                section_id="panel",
                edges=[
                    GridBarrierEdge(
                        first=GridPosition(x=2, y=1),
                        second=GridPosition(x=2, y=2),
                    ),
                    GridBarrierEdge(
                        first=GridPosition(x=3, y=1),
                        second=GridPosition(x=3, y=2),
                    ),
                ],
                current_hp=20,
                armor_class=15,
            ),
        ],
    )


def test_live_barrier_blocks_line_of_effect_and_destroyed_panel_reopens_it() -> None:
    source = _member("source", "heroes", 2, 0)
    target = _member("target", "monsters", 2, 3)
    wall = _wall()
    setup = EncounterSetup(
        heroes=[source],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1/4",
        map_definition=build_standard_iron_pit_map(),
        persistent_barriers=[wall],
    )

    assert not clear_line_between_members(source, target, setup)
    assert barrier_blocks_transition(
        GridPosition(x=2, y=1),
        GridPosition(x=2, y=2),
        setup.persistent_barriers,
    )

    wall.sections[0].destroyed = True
    wall.sections[0].current_hp = 0

    assert clear_line_between_members(source, target, setup)


def test_line_of_effect_is_noop_for_legacy_non_grid_encounters() -> None:
    source = EncounterCombatant(
        combatant_id="source",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_goblin_warrior()),
    )
    target = EncounterCombatant(
        combatant_id="target",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(build_goblin_warrior()),
    )
    setup = EncounterSetup(
        heroes=[source],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1/4",
    )

    assert clear_line_between_members(source, target, setup)
