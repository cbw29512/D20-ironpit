import pytest

from app.combat.bonus_actions import use_nimble_escape_disengage
from app.combat.dice import FixedDiceProvider
from app.combat.disengage import take_disengage_action
from app.combat.reactions import retreat_with_opportunity_check
from app.combat.state import begin_turn, build_combatant_state, end_turn
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import BattlefieldState, ConditionKind


def test_standard_disengage_spends_action_for_rest_of_turn() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(fighter)

    event = take_disengage_action(1, 1, fighter, battlefield)

    assert event.event_type == "disengage"
    assert event.feature_id == "disengage"
    assert fighter.action_available is False
    assert fighter.bonus_action_available is True
    assert fighter.disengaged is True
    end_turn(fighter)
    assert fighter.disengaged is False


def test_standard_disengage_suppresses_opportunity_attack_during_movement() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(fighter)
    begin_turn(goblin)
    take_disengage_action(1, 1, fighter, battlefield)

    events, next_sequence = retreat_with_opportunity_check(
        2, 1, fighter, goblin, battlefield, FixedDiceProvider([20])
    )

    assert [event.event_type for event in events] == ["movement"]
    assert battlefield.distance_ft == 35
    assert goblin.reaction_available is True
    assert next_sequence == 3


def test_incapacitated_creature_cannot_take_disengage_action() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    fighter.conditions.add(ConditionKind.INCAPACITATED)

    with pytest.raises(ValueError, match="Incapacitated"):
        take_disengage_action(1, 1, fighter, BattlefieldState())


def test_nimble_escape_reuses_disengage_without_spending_action() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    event = use_nimble_escape_disengage(1, 1, goblin, battlefield)

    assert event.feature_id == "nimble-escape"
    assert goblin.action_available is True
    assert goblin.bonus_action_available is False
    assert goblin.disengaged is True
