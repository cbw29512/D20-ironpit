from app.combat.attacks import resolve_attack
from app.combat.conditions import apply_condition
from app.combat.d20_tests import resolve_saving_throw
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import Ability, ConditionType, RollMode


def test_restrained_speed_is_zero_but_action_remains_available() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.RESTRAINED)

    begin_turn(fighter)

    assert fighter.movement_remaining_ft == 0
    assert fighter.action_available is True
    assert fighter.bonus_action_available is True


def test_restrained_attacker_has_disadvantage() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    apply_condition(fighter, ConditionType.RESTRAINED)

    event = resolve_attack(
        1,
        1,
        fighter,
        goblin,
        fighter.template.weapon_attack,
        5,
        FixedDiceProvider([14, 4]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.hit is False


def test_attack_against_restrained_target_has_advantage() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    apply_condition(goblin, ConditionType.RESTRAINED)

    event = resolve_attack(
        1,
        1,
        fighter,
        goblin,
        fighter.template.weapon_attack,
        5,
        FixedDiceProvider([4, 14, 3]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.hit is True


def test_restrained_only_penalizes_dexterity_saving_throws() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.RESTRAINED)
    dice = FixedDiceProvider([18, 4, 10])

    dex_roll, dex_success = resolve_saving_throw(
        fighter, Ability.DEXTERITY, 10, dice
    )
    strength_roll, strength_success = resolve_saving_throw(
        fighter, Ability.STRENGTH, 10, dice
    )

    assert dex_roll is not None
    assert dex_roll.mode is RollMode.DISADVANTAGE
    assert dex_roll.selected_roll == 4
    assert dex_success is False
    assert strength_roll is not None
    assert strength_roll.mode is RollMode.NORMAL
    assert strength_success is True
