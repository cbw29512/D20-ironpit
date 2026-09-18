from app.combat.forced_movement import push_straight_away
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition

MAP = BattleMapDefinition(id="forced-movement", width_squares=8, height_squares=8)


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(update={"id": combatant_id, "name": combatant_id})
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    state.movement_remaining_ft = 30
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)


def _setup(source, target, *extra):
    return EncounterSetup(
        heroes=[source], monsters=[target, *extra], hero_total_levels=1,
        monster_total_cr="1/4", map_definition=MAP,
    )


def test_push_straight_away_moves_three_squares_without_spending_speed():
    source = _member("source", "heroes", 1, 1)
    target = _member("target", "monsters", 2, 1)
    setup = _setup(source, target)
    assert push_straight_away(target, source, setup, 15) == 15
    assert target.state.position == GridPosition(x=5, y=1)
    assert target.state.movement_remaining_ft == 30


def test_push_straight_away_preserves_non_diagonal_source_ray():
    source = _member("source", "heroes", 1, 1)
    target = _member("target", "monsters", 3, 2)
    setup = _setup(source, target)
    assert push_straight_away(target, source, setup, 5) == 5
    assert target.state.position == GridPosition(x=5, y=3)


def test_push_straight_away_stops_before_occupied_space():
    source = _member("source", "heroes", 1, 1)
    target = _member("target", "monsters", 2, 1)
    blocker = _member("blocker", "monsters", 4, 1)
    setup = _setup(source, target, blocker)
    assert push_straight_away(target, source, setup, 15) == 5
    assert target.state.position == GridPosition(x=3, y=1)


def test_push_straight_away_stops_at_map_boundary():
    source = _member("source", "heroes", 5, 1)
    target = _member("target", "monsters", 6, 1)
    setup = _setup(source, target)
    assert push_straight_away(target, source, setup, 15) == 5
    assert target.state.position == GridPosition(x=7, y=1)
