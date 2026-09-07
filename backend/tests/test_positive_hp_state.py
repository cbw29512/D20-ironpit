from app.combat.hit_points import set_positive_hit_points
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior


def test_positive_hp_transition_is_one_shared_state_mutation() -> None:
    state = build_combatant_state(build_goblin_warrior())
    state.current_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = True
    state.is_stable = True
    state.death_save_successes = 2
    state.death_save_failures = 2

    assert set_positive_hit_points(state, 1) == 1
    assert state.current_hp == 1
    assert state.is_alive is True
    assert state.is_dead is False
    assert state.is_unconscious is False
    assert state.is_stable is False
    assert state.death_save_successes == 0
    assert state.death_save_failures == 0
