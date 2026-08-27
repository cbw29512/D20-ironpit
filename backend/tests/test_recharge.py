import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.recharge import get_recharge_state, roll_recharges
from app.combat.save_actions import resolve_save_action
from app.combat.state import build_combatant_state
from app.combat.turn_execution import execute_turn
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import Ability, BattlefieldState, RechargeDefinition, SaveAction


def _recharge_actor():
    template = build_demo_fighter().model_copy(update={
        "save_actions": [SaveAction(
            id="test-recharge",
            name="Test Recharge",
            save_ability=Ability.WISDOM,
            dc=10,
            range_ft=30,
            recharge=RechargeDefinition(min_roll=5, max_roll=6),
        )]
    })
    return build_combatant_state(template, "actor-1")


def test_recharge_action_spends_and_restores_on_five_or_six() -> None:
    actor = _recharge_actor()
    target = build_combatant_state(build_goblin_warrior(), "target-1")
    action = actor.template.save_actions[0]

    resolve_save_action(1, 1, actor, target, 5, action, FixedDiceProvider([15]))
    state = get_recharge_state(actor, action.id)
    assert state is not None
    assert state.available is False

    actor.action_available = True
    with pytest.raises(ValueError, match="has not recharged"):
        resolve_save_action(2, 1, actor, target, 5, action, FixedDiceProvider([15]))

    failed = roll_recharges(2, 2, actor, FixedDiceProvider([4]))
    assert failed[0].event_type == "recharge"
    assert failed[0].recharge_roll is not None
    assert failed[0].recharge_roll.selected_roll == 4
    assert failed[0].test_success is False
    assert state.available is False

    restored = roll_recharges(3, 3, actor, FixedDiceProvider([5]))
    assert restored[0].recharge_roll is not None
    assert restored[0].recharge_roll.selected_roll == 5
    assert restored[0].test_success is True
    assert state.available is True


def test_turn_start_emits_recharge_before_action() -> None:
    actor = _recharge_actor()
    target = build_combatant_state(build_goblin_warrior(), "target-1")
    state = get_recharge_state(actor, "test-recharge")
    assert state is not None
    state.available = False

    events, _ = execute_turn(
        1,
        2,
        actor,
        target,
        BattlefieldState(distance_ft=5),
        FixedDiceProvider([5, 20, 4, 4]),
    )

    assert events[0].event_type == "recharge"
    assert events[0].test_success is True
    assert state.available is True
    assert next(event for event in events if event.event_type == "attack").critical is True
