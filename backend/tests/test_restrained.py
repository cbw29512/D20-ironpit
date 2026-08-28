from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.dodge import has_dodge_benefits, take_dodge_action
from app.combat.movement import move_toward_target, take_dash
from app.combat.saving_throws import resolve_saving_throw
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import AbilityKind, BattlefieldState, ConditionKind, RollMode


def restrain(state):
    state.conditions.add(ConditionKind.RESTRAINED)
    return state


def test_restrained_speed_is_zero_at_turn_start_and_mid_turn() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=20)
    begin_turn(fighter)
    assert fighter.movement_remaining_ft == 30

    restrain(fighter)
    assert move_toward_target(1, 1, fighter, battlefield, 5) is None
    begin_turn(fighter)
    assert fighter.movement_remaining_ft == 0


def test_attacks_against_restrained_target_have_advantage() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = restrain(build_combatant_state(build_goblin_warrior()))

    event = resolve_attack(
        1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([5, 18, 4]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 18


def test_restrained_creatures_can_act_but_their_attacks_have_disadvantage() -> None:
    fighter = restrain(build_combatant_state(build_demo_fighter()))
    goblin = build_combatant_state(build_goblin_warrior())

    event = resolve_attack(
        1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([18, 5]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.selected_roll == 5
    assert fighter.action_available is False


def test_restrained_attacker_and_defender_cancel_to_normal_attack_roll() -> None:
    fighter = restrain(build_combatant_state(build_demo_fighter()))
    goblin = restrain(build_combatant_state(build_goblin_warrior()))

    event = resolve_attack(
        1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([10, 4]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL
    assert event.attack_roll.rolls == [10]


def test_restrained_dexterity_save_has_disadvantage_but_other_saves_do_not() -> None:
    goblin = restrain(build_combatant_state(build_goblin_warrior()))

    dexterity = resolve_saving_throw(
        goblin, AbilityKind.DEXTERITY, 10, FixedDiceProvider([18, 5])
    )
    wisdom = resolve_saving_throw(
        goblin, AbilityKind.WISDOM, 10, FixedDiceProvider([11])
    )

    assert dexterity.roll is not None
    assert dexterity.roll.mode is RollMode.DISADVANTAGE
    assert dexterity.roll.selected_roll == 5
    assert wisdom.roll is not None
    assert wisdom.roll.mode is RollMode.NORMAL


def test_restrained_dexterity_disadvantage_cancels_other_advantage() -> None:
    goblin = restrain(build_combatant_state(build_goblin_warrior()))

    result = resolve_saving_throw(
        goblin,
        AbilityKind.DEXTERITY,
        14,
        FixedDiceProvider([12]),
        advantage_sources=1,
    )

    assert result.roll is not None
    assert result.roll.mode is RollMode.NORMAL
    assert result.roll.total == 14


def test_restrained_speed_zero_suppresses_active_dodge_benefits() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    take_dodge_action(1, 1, goblin)
    restrain(goblin)

    event = resolve_attack(
        2, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([5, 18, 4]),
    )

    assert goblin.dodging is True
    assert has_dodge_benefits(goblin) is False
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE


def test_restrained_creature_can_dash_but_speed_zero_grants_no_extra_movement() -> None:
    fighter = restrain(build_combatant_state(build_demo_fighter()))
    battlefield = BattlefieldState(distance_ft=20)
    begin_turn(fighter)

    event = take_dash(1, 1, fighter, battlefield)

    assert event.movement_ft == 0
    assert fighter.action_available is False
    assert fighter.movement_remaining_ft == 0
