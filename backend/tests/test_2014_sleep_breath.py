from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.encounter_setup import build_encounter_setup
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.models import EncounterSelection


def _setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-commoner"],
    ))
    return setup, setup.heroes[0], setup.heroes[1]


def _sleep(target) -> None:
    apply_timed_condition(
        target.state, "unconscious", "dragon-1",
        source_effect_id="sleep-breath", applied_round=1, expires_round=11,
        expiry_timing="source_turn_start", allowed_removal_action_ids=["wake-sleeper"],
        ends_on_damage=True,
    )


def test_sleep_breath_can_be_woken_by_adjacent_ally_action() -> None:
    setup, ally, sleeper = _setup()
    _sleep(sleeper)
    choice = choose_condition_removal_action(ally, setup, "1:ally")
    assert choice is not None
    action, target, conditions = choice
    assert action.id == "wake-sleeper"
    assert target is sleeper
    assert conditions == ["unconscious"]
    resolve_condition_removal(1, 1, ally, target, action, conditions, "1:ally")
    assert ally.state.action_available is False
    assert "unconscious" not in sleeper.state.active_effect_ids


def test_sleep_breath_ends_when_target_takes_damage() -> None:
    _, _, sleeper = _setup()
    _sleep(sleeper)
    hp_before = sleeper.state.current_hp
    assert apply_damage(sleeper.state, 1) == "damaged"
    assert sleeper.state.current_hp == hp_before - 1
    assert "unconscious" not in sleeper.state.active_effect_ids
    assert not any(effect.source_effect_id == "sleep-breath" for effect in sleeper.state.timed_effects)
