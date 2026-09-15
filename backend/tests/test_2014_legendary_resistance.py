from app.combat.dice import FixedDiceProvider
from app.combat.legendary_resistance import legendary_resistance_remaining
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.monster_catalog_2014 import MVP_CATALOG_PATH, compile_monster_2014, load_catalog_2014
from app.content.monster_catalog_2014_traits import legendary_resistance_uses_2014, unresolved_traits_2014


def test_legendary_resistance_parses_exact_daily_uses() -> None:
    names = ["Legendary Resistance (3/Day)"]
    assert legendary_resistance_uses_2014(names) == 3
    assert unresolved_traits_2014(names) == []


def test_first_three_failed_saves_auto_succeed_and_fourth_fails() -> None:
    source = next(monster for monster in load_catalog_2014(MVP_CATALOG_PATH) if monster.id == "bandit")
    source = source.model_copy(update={"trait_names": ["Legendary Resistance (3/Day)"]})
    state = build_combatant_state(compile_monster_2014(source))
    dice = FixedDiceProvider([1, 1, 1, 1])

    outcomes = [resolve_saving_throw(state, "wisdom", 30, dice)[1] for _ in range(4)]

    assert outcomes == [True, True, True, False]
    assert legendary_resistance_remaining(state) == 0


def test_successful_save_does_not_spend_legendary_resistance() -> None:
    source = next(monster for monster in load_catalog_2014(MVP_CATALOG_PATH) if monster.id == "bandit")
    source = source.model_copy(update={"trait_names": ["Legendary Resistance (3/Day)"]})
    state = build_combatant_state(compile_monster_2014(source))

    _, succeeded = resolve_saving_throw(state, "dexterity", 1, FixedDiceProvider([20]))

    assert succeeded is True
    assert legendary_resistance_remaining(state) == 3
