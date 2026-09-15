from app.combat.death_saves import resolve_death_save
from app.combat.dice import FixedDiceProvider
from app.combat.progression_recovery import resolve_bloodied_start_turn_healing
from app.combat.state import build_combatant_state
from app.content.fighter_progression import build_karnok_stoneward_level


def _survivor_state():
    state = build_combatant_state(build_karnok_stoneward_level(18))
    return state


def test_survivor_compiles_as_generic_progression_data() -> None:
    template = build_karnok_stoneward_level(18)
    features = template.progression_features

    assert features.death_save_advantage is True
    assert features.death_save_recovery_minimum == 18
    assert features.bloodied_start_turn_healing_base == 5
    assert features.bloodied_start_turn_healing_add_constitution is True


def test_survivor_death_save_uses_advantage_and_recovers_on_18() -> None:
    state = _survivor_state()
    state.current_hp = 0
    state.is_unconscious = True

    event = resolve_death_save(1, 1, "karnok", state, FixedDiceProvider([7, 18]))

    assert event.death_save_roll is not None
    assert event.death_save_roll.rolls == [7, 18]
    assert event.death_save_roll.selected_roll == 18
    assert event.death_save_roll.mode == "advantage"
    assert state.current_hp == 1
    assert state.is_unconscious is False


def test_survivor_heroic_rally_heals_only_when_alive_and_bloodied() -> None:
    state = _survivor_state()
    state.current_hp = state.template.max_hp // 2

    healed = resolve_bloodied_start_turn_healing(state)

    assert healed == 10
    assert state.current_hp == state.template.max_hp // 2 + 10

    state.current_hp = 0
    assert resolve_bloodied_start_turn_healing(state) == 0
