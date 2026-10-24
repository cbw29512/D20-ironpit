from app.combat.forced_movement import push_straight_away, pull_straight_toward
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


def test_push_and_pull_ignore_displacement_and_preserve_combat_state():
    source = _member("source", "heroes", 1, 1)
    target = _member("target", "monsters", 2, 1)
    setup = _setup(source, target)
    original = target.state.position.model_copy(deep=True)
    hp = target.state.current_hp
    assert push_straight_away(target, source, setup, 15) == 0
    assert pull_straight_toward(target, source, setup, 10) == 0
    assert target.state.position == original
    assert target.state.movement_remaining_ft == 30
    assert target.state.current_hp == hp


def test_forced_movement_does_not_need_grid_position_to_be_ignored():
    source = _member("source", "heroes", 1, 1)
    target = _member("target", "monsters", 2, 1)
    setup = _setup(source, target)
    target.state.position = None
    assert push_straight_away(target, source, setup, 5) == 0
    assert pull_straight_toward(target, source, setup, 5) == 0
