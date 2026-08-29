import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.saving_throws import legal_save_action, resolve_save_action, resolve_saving_throw
from app.domain.models import DamageType, EncounterSelection, RollMode


def _state(hero_id="karnok-stoneward-l1"):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=[hero_id], monster_ids=["srd-commoner"], starting_distance_ft=5,
    ))
    return setup.heroes[0].state


def _constrict_setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-constrictor-snake"], starting_distance_ft=5,
    ))
    return setup, setup.heroes[0], setup.monsters[0]


def test_saving_throws_do_not_use_attack_nat_one_or_nat_twenty_rules() -> None:
    state = _state()
    high_roll, high_success = resolve_saving_throw(state, "intelligence", 20, FixedDiceProvider([20]))
    low_roll, low_success = resolve_saving_throw(state, "strength", 6, FixedDiceProvider([1]))
    assert high_roll is not None and high_roll.total == 19 and high_success is False
    assert low_roll is not None and low_roll.total == 6 and low_success is True


def test_restrained_dexterity_save_has_disadvantage() -> None:
    state = _state()
    state.active_effect_ids.append("restrained")
    roll, succeeded = resolve_saving_throw(state, "dexterity", 10, FixedDiceProvider([18, 2]))
    assert roll is not None and roll.mode is RollMode.DISADVANTAGE
    assert roll.selected_roll == 2 and succeeded is False


def test_rage_strength_save_has_advantage() -> None:
    state = _state("rokhan-stonefury-l1")
    state.active_effect_ids.append("rage")
    roll, succeeded = resolve_saving_throw(state, "strength", 12, FixedDiceProvider([2, 10]))
    assert roll is not None and roll.mode is RollMode.ADVANTAGE
    assert roll.selected_roll == 10 and succeeded is True


def test_unconscious_auto_fails_strength_and_dexterity_saves() -> None:
    state = _state()
    state.current_hp = 0
    state.is_unconscious = True
    strength_roll, strength_success = resolve_saving_throw(state, "strength", 1, FixedDiceProvider([20]))
    dex_roll, dex_success = resolve_saving_throw(state, "dexterity", 1, FixedDiceProvider([20]))
    assert strength_roll is None and strength_success is False
    assert dex_roll is None and dex_success is False


def test_missing_save_bonus_fails_closed() -> None:
    state = _state()
    state.template.saving_throw_bonuses = {}
    with pytest.raises(ValueError, match="lacks a certified"):
        resolve_saving_throw(state, "wisdom", 10, FixedDiceProvider([10]))


def test_constrict_failure_deals_damage_and_grapples() -> None:
    _, hero, snake = _constrict_setup()
    action = snake.state.template.saving_throw_actions[0]
    event = resolve_save_action(1, 1, snake, hero, action, 5, FixedDiceProvider([1, 1, 2, 3]))
    assert event.save_succeeded is False
    assert event.damage_roll is not None and event.damage_roll.total == 6
    assert hero.state.current_hp == 6
    assert event.applied_condition_ids == ["grappled"]
    assert hero.state.grapple_sources[0].escape_dc == 12


def test_constrict_success_rolls_no_damage_and_applies_no_grapple() -> None:
    _, hero, snake = _constrict_setup()
    action = snake.state.template.saving_throw_actions[0]
    event = resolve_save_action(1, 1, snake, hero, action, 5, FixedDiceProvider([10]))
    assert event.save_succeeded is True
    assert event.damage_roll is None and event.damage_components == []
    assert hero.state.current_hp == hero.state.template.max_hp
    assert hero.state.grapple_sources == []


def test_half_damage_on_success_precedes_resistance() -> None:
    _, hero, snake = _constrict_setup()
    hero.state.template.damage_resistances = [DamageType.FIRE]
    action = snake.state.template.saving_throw_actions[0].model_copy(update={
        "damage_dice_count": 2,
        "damage_dice_size": 6,
        "damage_type": "fire",
        "success_damage": "half",
    })
    event = resolve_save_action(1, 1, snake, hero, action, 5, FixedDiceProvider([10, 5, 6]))
    assert event.save_succeeded is True
    assert event.damage_roll is not None and event.damage_roll.total == 2
    assert event.damage_components[0].total == 5
    assert event.damage_components[0].applied_total == 2
    assert hero.state.current_hp == 10


def test_constrict_rider_still_applies_when_damage_knocks_character_unconscious() -> None:
    _, hero, snake = _constrict_setup()
    hero.state.current_hp = 1
    resource = next(item for item in hero.state.resources if item.id == "relentless-endurance")
    resource.current_uses = 0
    action = snake.state.template.saving_throw_actions[0]
    event = resolve_save_action(1, 1, snake, hero, action, 5, FixedDiceProvider([1, 1, 1, 1]))
    assert hero.state.current_hp == 0 and hero.state.is_unconscious is True
    assert event.applied_condition_ids == ["grappled"]
    assert hero.state.grapple_sources[0].source_id == snake.combatant_id


def test_constrict_rejects_large_target() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-constrictor-snake", "srd-crocodile"], starting_distance_ft=5,
    ))
    snake, crocodile = setup.monsters
    action = snake.state.template.saving_throw_actions[0]
    assert legal_save_action(action, setup.heroes[0], 5) is True
    assert legal_save_action(action, crocodile, 5) is False
