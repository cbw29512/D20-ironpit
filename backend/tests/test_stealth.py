import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.initiative import roll_initiative_order
from app.combat.search import take_search_action
from app.combat.state import begin_turn, build_combatant_state
from app.combat.stealth import can_hide, take_hide_action
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import (
    ActorVisibilityState,
    BattlefieldState,
    ConditionKind,
    CoverLevel,
    RollMode,
)


def hiding_battlefield(actor_id: str, *, cover=CoverLevel.THREE_QUARTERS):
    return BattlefieldState(
        distance_ft=30,
        visibility_by_actor={
            actor_id: ActorVisibilityState(
                cover=cover,
                enemy_line_of_sight=False,
            )
        },
    )


def test_open_arena_does_not_allow_hide() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=30)

    assert can_hide(goblin, battlefield) is False
    with pytest.raises(ValueError, match="Hide requires concealment"):
        take_hide_action(1, 1, goblin, battlefield, FixedDiceProvider([20]))


def test_hide_requires_concealment_and_no_enemy_line_of_sight() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    blocked = BattlefieldState(
        distance_ft=30,
        visibility_by_actor={
            goblin.template.id: ActorVisibilityState(
                cover=CoverLevel.TOTAL,
                enemy_line_of_sight=True,
            )
        },
    )
    obscured = BattlefieldState(
        distance_ft=30,
        visibility_by_actor={
            goblin.template.id: ActorVisibilityState(
                heavily_obscured=True,
                enemy_line_of_sight=False,
            )
        },
    )

    assert can_hide(goblin, blocked) is False
    assert can_hide(goblin, obscured) is True


def test_successful_hide_uses_dc_15_and_grants_invisible_while_hidden() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = hiding_battlefield(goblin.template.id)
    begin_turn(goblin)

    event = take_hide_action(1, 1, goblin, battlefield, FixedDiceProvider([9]))

    assert event.check_roll is not None
    assert event.check_roll.total == 15
    assert goblin.hidden is True
    assert goblin.hidden_dc == 15
    assert ConditionKind.INVISIBLE in goblin.conditions
    assert goblin.action_available is False


def test_failed_hide_consumes_action_without_granting_invisible() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = hiding_battlefield(goblin.template.id)
    begin_turn(goblin)

    event = take_hide_action(1, 1, goblin, battlefield, FixedDiceProvider([8]))

    assert event.check_roll is not None
    assert event.check_roll.total == 14
    assert goblin.hidden is False
    assert ConditionKind.INVISIBLE not in goblin.conditions
    assert goblin.action_available is False


def test_hidden_attacker_has_advantage_and_reveals_after_attack_roll() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = hiding_battlefield(goblin.template.id)
    begin_turn(goblin)
    take_hide_action(1, 1, goblin, battlefield, FixedDiceProvider([10]))
    begin_turn(goblin)

    event = resolve_attack(
        2, 2, goblin, fighter, goblin.template.alternate_weapon_attacks[0], 30,
        FixedDiceProvider([4, 17, 3, 2]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.rolls == [4, 17]
    assert goblin.hidden is False
    assert ConditionKind.INVISIBLE not in goblin.conditions
    assert event.damage_roll is not None
    assert event.damage_roll.total == 7


def test_attack_against_hidden_defender_has_disadvantage_without_revealing_it() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = hiding_battlefield(goblin.template.id)
    begin_turn(goblin)
    take_hide_action(1, 1, goblin, battlefield, FixedDiceProvider([10]))
    begin_turn(fighter)

    event = resolve_attack(
        2, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([18, 7]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.rolls == [18, 7]
    assert goblin.hidden is True
    assert ConditionKind.INVISIBLE in goblin.conditions


def test_search_uses_hidden_stealth_total_as_perception_dc() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = hiding_battlefield(goblin.template.id)
    begin_turn(goblin)
    take_hide_action(1, 1, goblin, battlefield, FixedDiceProvider([10]))
    assert goblin.hidden_dc == 16

    begin_turn(fighter)
    failed = take_search_action(2, 1, fighter, goblin, FixedDiceProvider([15]))
    assert failed.check_roll is not None
    assert goblin.hidden is True

    begin_turn(fighter)
    found = take_search_action(3, 2, fighter, goblin, FixedDiceProvider([16]))
    assert found.check_roll is not None
    assert goblin.hidden is False
    assert goblin.hidden_dc is None
    assert ConditionKind.INVISIBLE not in goblin.conditions


def test_invisible_condition_grants_advantage_on_initiative() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    fighter.conditions.add(ConditionKind.INVISIBLE)

    events, _, _ = roll_initiative_order(
        (fighter, goblin), FixedDiceProvider([3, 17, 10])
    )

    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.ADVANTAGE
    assert events[0].attack_roll.rolls == [3, 17]
