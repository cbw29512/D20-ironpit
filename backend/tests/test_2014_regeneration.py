from app.combat.dice import FixedDiceProvider
from app.combat.regeneration import resolve_start_turn
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.demo import build_goblin_warrior
from app.domain.regeneration import RegenerationProfile


def _state(profile: RegenerationProfile, hp: int):
    template = build_goblin_warrior().model_copy(update={"ruleset": "2014", "regeneration": profile, "max_hp": 30})
    state = build_combatant_state(template); state.current_hp = hp
    return state


def test_positive_hp_regeneration_heals_at_start_of_turn() -> None:
    state = _state(RegenerationProfile(amount=10, requires_positive_hp=True), 12)
    event, died = resolve_start_turn(1, 2, "monster-1", state)
    assert died is False and event is not None
    assert state.current_hp == 22
    assert event.hp_before == 12 and event.hp_after == 22


def test_suppressing_damage_skips_one_regeneration_check() -> None:
    state = _state(RegenerationProfile(amount=10, requires_positive_hp=True, suppressed_by_damage_types=["fire"]), 20)
    apply_damage(state, 3, damage_types={"fire"}, dice=FixedDiceProvider([]))
    event, died = resolve_start_turn(1, 2, "monster-1", state)
    assert event is None and died is False
    assert state.current_hp == 17 and state.regeneration_suppressed is False
    event, died = resolve_start_turn(1, 3, "monster-1", state)
    assert event is not None and state.current_hp == 27


def test_troll_style_regenerator_holds_at_zero_then_recovers() -> None:
    state = _state(RegenerationProfile(amount=10, suppressed_by_damage_types=["acid", "fire"], survives_zero_until_turn=True), 5)
    outcome = apply_damage(state, 8, damage_types={"slashing"}, dice=FixedDiceProvider([]))
    assert outcome == "regeneration_hold"
    assert state.current_hp == 0 and state.is_alive and not state.is_dead
    event, died = resolve_start_turn(1, 2, "troll", state)
    assert event is not None and died is False
    assert state.current_hp == 10 and state.is_alive and not state.is_unconscious


def test_troll_style_regenerator_dies_at_zero_when_suppressed() -> None:
    state = _state(RegenerationProfile(amount=10, suppressed_by_damage_types=["acid", "fire"], survives_zero_until_turn=True), 5)
    outcome = apply_damage(state, 8, damage_types={"fire"}, dice=FixedDiceProvider([]))
    assert outcome == "regeneration_hold" and state.regeneration_suppressed
    event, died = resolve_start_turn(1, 2, "troll", state)
    assert died is True and event is not None
    assert state.is_dead and not state.is_alive and state.current_hp == 0
