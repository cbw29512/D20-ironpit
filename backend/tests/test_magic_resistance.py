from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.saving_throw_rolls import resolve_saving_throw, saving_throw_mode
from app.domain.models import EncounterSelection, RollMode
from app.domain.traits import CombatTrait


def _state():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    state = setup.heroes[0].state
    state.template.combat_traits.append(CombatTrait.MAGIC_RESISTANCE)
    return state


def test_magic_resistance_grants_advantage_only_against_magic() -> None:
    state = _state()
    magical_roll, magical_success = resolve_saving_throw(
        state, "dexterity", 10, FixedDiceProvider([2, 18]), against_magic=True,
    )
    ordinary_roll, ordinary_success = resolve_saving_throw(
        state, "dexterity", 10, FixedDiceProvider([2]),
    )
    assert magical_roll is not None and magical_roll.mode is RollMode.ADVANTAGE
    assert magical_roll.selected_roll == 18 and magical_success is True
    assert ordinary_roll is not None and ordinary_roll.mode is RollMode.NORMAL
    assert ordinary_roll.selected_roll == 2 and ordinary_success is False


def test_magic_resistance_uses_normal_advantage_disadvantage_cancellation() -> None:
    state = _state()
    state.active_effect_ids.append("restrained")
    assert saving_throw_mode(state, "dexterity", against_magic=True) is RollMode.NORMAL


def test_magic_resistance_does_not_change_nonmagical_save_mode() -> None:
    state = _state()
    assert saving_throw_mode(state, "wisdom") is RollMode.NORMAL
