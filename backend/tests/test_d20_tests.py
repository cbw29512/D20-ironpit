import pytest

from app.combat.d20_tests import (
    choose_best_save,
    resolve_ability_check,
    resolve_saving_throw,
    saving_throw_modifier,
)
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import Ability, Skill


def test_saving_throw_uses_explicit_proficiency_modifier() -> None:
    fighter = build_combatant_state(build_demo_fighter())

    roll, success = resolve_saving_throw(
        fighter, Ability.STRENGTH, 15, FixedDiceProvider([10])
    )

    assert roll.modifier == 5
    assert roll.total == 15
    assert success is True


def test_saving_throw_falls_back_to_ability_modifier() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    roll, success = resolve_saving_throw(
        goblin, Ability.DEXTERITY, 13, FixedDiceProvider([10])
    )

    assert roll.modifier == 2
    assert success is False


def test_save_has_no_attack_style_auto_success_on_natural_twenty() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    roll, success = resolve_saving_throw(
        goblin, Ability.STRENGTH, 25, FixedDiceProvider([20])
    )

    assert roll.total == 19
    assert success is False


def test_best_save_policy_chooses_higher_legal_modifier() -> None:
    fighter = build_combatant_state(build_demo_fighter())

    chosen = choose_best_save(fighter, (Ability.STRENGTH, Ability.DEXTERITY))

    assert chosen is Ability.STRENGTH
    assert saving_throw_modifier(fighter, chosen) == 5


def test_escape_style_ability_check_uses_skill_modifier() -> None:
    fighter = build_combatant_state(build_demo_fighter())

    roll, success = resolve_ability_check(
        fighter, Skill.ATHLETICS, 14, FixedDiceProvider([9])
    )

    assert roll.modifier == 5
    assert roll.total == 14
    assert success is True


def test_missing_ability_data_fails_closed() -> None:
    template = build_goblin_warrior().model_copy(update={"ability_modifiers": {}})
    state = build_combatant_state(template)

    with pytest.raises(ValueError, match="Missing strength"):
        resolve_saving_throw(state, Ability.STRENGTH, 10, FixedDiceProvider([10]))
