import pytest

from app.combat.attacks import resolve_attack
from app.combat.bonus_actions import use_nimble_escape_disengage
from app.combat.dice import FixedDiceProvider
from app.combat.fighter import use_second_wind
from app.combat.initiative import roll_initiative_order
from app.combat.movement import move_toward_target, take_dash
from app.combat.reactions import resolve_opportunity_attack
from app.combat.state import begin_turn, build_combatant_state
from app.combat.stealth import take_hide_action
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import (
    ActorVisibilityState,
    BattlefieldState,
    ConditionKind,
    CoverLevel,
    RollMode,
)


def incapacitate(state):
    state.conditions.add(ConditionKind.INCAPACITATED)
    return state


def test_incapacitated_imposes_initiative_disadvantage() -> None:
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))

    events, _, _ = roll_initiative_order([fighter], FixedDiceProvider([18, 5]))

    roll = events[0].attack_roll
    assert roll is not None
    assert roll.mode is RollMode.DISADVANTAGE
    assert roll.rolls == [18, 5]
    assert roll.selected_roll == 5


def test_invisible_and_incapacitated_cancel_on_initiative() -> None:
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))
    fighter.conditions.add(ConditionKind.INVISIBLE)

    events, _, _ = roll_initiative_order([fighter], FixedDiceProvider([12]))

    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.NORMAL


def test_incapacitated_creature_cannot_attack() -> None:
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))
    goblin = build_combatant_state(build_goblin_warrior())

    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        resolve_attack(
            1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
            FixedDiceProvider([20]),
        )


def test_incapacitated_enemy_does_not_impose_close_ranged_disadvantage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))
    shortbow = goblin.template.alternate_weapon_attacks[0]

    event = resolve_attack(
        1, 1, goblin, fighter, shortbow, 5, FixedDiceProvider([10])
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL


def test_incapacitated_creature_cannot_make_opportunity_attack() -> None:
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))
    goblin = build_combatant_state(build_goblin_warrior())

    event = resolve_opportunity_attack(
        1, 1, fighter, goblin, 5, 35, FixedDiceProvider([20])
    )

    assert event is None
    assert fighter.reaction_available is True


def test_incapacitated_blocks_bonus_action_features() -> None:
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))
    goblin = incapacitate(build_combatant_state(build_goblin_warrior()))
    fighter.current_hp = 5

    with pytest.raises(RuntimeError, match="Second Wind could not be resolved"):
        use_second_wind(1, 1, fighter, FixedDiceProvider([5]))
    with pytest.raises(ValueError, match="Incapacitated"):
        use_nimble_escape_disengage(1, 1, goblin, BattlefieldState())


def test_incapacitated_blocks_hide_and_dash_actions() -> None:
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))
    battlefield = BattlefieldState(
        distance_ft=30,
        visibility_by_actor={
            fighter.template.id: ActorVisibilityState(
                cover=CoverLevel.THREE_QUARTERS,
                enemy_line_of_sight=False,
            )
        },
    )
    begin_turn(fighter)

    with pytest.raises(ValueError, match="Incapacitated"):
        take_hide_action(1, 1, fighter, battlefield, FixedDiceProvider([20]))
    with pytest.raises(ValueError, match="Incapacitated"):
        take_dash(1, 1, fighter, battlefield)


def test_incapacitated_alone_does_not_remove_normal_movement() -> None:
    fighter = incapacitate(build_combatant_state(build_demo_fighter()))
    battlefield = BattlefieldState(distance_ft=20)
    begin_turn(fighter)

    event = move_toward_target(1, 1, fighter, battlefield, 5)

    assert event is not None
    assert event.movement_ft == 15
    assert battlefield.distance_ft == 5
