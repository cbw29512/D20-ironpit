import pytest

from app.combat.conditions import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.save_actions import resolve_save_action
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import (
    Ability,
    ConditionExpiry,
    ConditionType,
    SaveAction,
    SaveFailureEffect,
)


def _fear_action() -> SaveAction:
    return SaveAction(
        id="test-fear",
        name="Test Fear",
        save_ability=Ability.WISDOM,
        dc=11,
        range_ft=15,
        failure_effects=[SaveFailureEffect(
            condition=ConditionType.FRIGHTENED,
            expires_on=ConditionExpiry.SOURCE_TURN_START,
        )],
    )


def test_failed_save_applies_timed_condition() -> None:
    actor = build_combatant_state(build_goblin_warrior(), "source-1")
    target = build_combatant_state(build_demo_fighter(), "target-1")
    begin_turn(actor)

    events = resolve_save_action(
        1, 1, actor, target, 10, _fear_action(), FixedDiceProvider([5])
    )

    assert [event.event_type for event in events] == ["saving_throw", "condition"]
    assert events[0].test_success is False
    assert has_condition(target, ConditionType.FRIGHTENED)
    condition = target.conditions[0]
    assert condition.source_id == "source-1"
    assert condition.expires_on is ConditionExpiry.SOURCE_TURN_START
    assert actor.action_available is False


def test_successful_save_applies_no_failure_effect() -> None:
    actor = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    begin_turn(actor)

    events = resolve_save_action(
        1, 1, actor, target, 10, _fear_action(), FixedDiceProvider([20])
    )

    assert len(events) == 1
    assert events[0].test_success is True
    assert not has_condition(target, ConditionType.FRIGHTENED)


def test_save_action_enforces_range_before_spending_action() -> None:
    actor = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    begin_turn(actor)

    with pytest.raises(ValueError, match="out of range"):
        resolve_save_action(
            1, 1, actor, target, 20, _fear_action(), FixedDiceProvider([1])
        )

    assert actor.action_available is True


def test_save_action_requires_available_action() -> None:
    actor = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_fighter())
    begin_turn(actor)
    actor.action_available = False

    with pytest.raises(ValueError, match="Action is not available"):
        resolve_save_action(
            1, 1, actor, target, 10, _fear_action(), FixedDiceProvider([1])
        )
