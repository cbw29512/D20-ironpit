from types import SimpleNamespace

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.resources import (
    build_recharge_events,
    can_use_action_resource,
    refresh_recharge_resources,
    spend_action_resource,
)
from app.domain.combatants import ResourceDefinition
from app.domain.events import AuditPhase
from app.domain.runtime import ResourceState


def _state(*, current: int = 1, recharge_minimum: int | None = 5):
    definition = ResourceDefinition(
        id="breath", name="Breath Weapon", max_uses=1,
        recharge_minimum=recharge_minimum, recharge_die_size=6,
    )
    return SimpleNamespace(
        template=SimpleNamespace(kind="monster", name="Test Dragon", resources=[definition]),
        resources=[ResourceState(id="breath", name="Breath Weapon", current_uses=current, max_uses=1)],
    )


def test_action_resource_spends_and_blocks_when_empty() -> None:
    state = _state()
    action = SimpleNamespace(id="fire-breath", resource_id="breath", resource_cost=1)
    assert can_use_action_resource(state, action)
    assert spend_action_resource(state, action) == 0
    assert not can_use_action_resource(state, action)
    with pytest.raises(ValueError, match="unavailable"):
        spend_action_resource(state, action)


def test_recharge_only_restores_on_threshold() -> None:
    state = _state(current=0)
    failed = refresh_recharge_resources(state, FixedDiceProvider([4]))
    assert failed[0].roll == 4 and not failed[0].recharged
    assert state.resources[0].current_uses == 0
    succeeded = refresh_recharge_resources(state, FixedDiceProvider([5]))
    assert succeeded[0].roll == 5 and succeeded[0].recharged
    assert state.resources[0].current_uses == 1


def test_recharge_result_becomes_auditable_resource_event() -> None:
    state = _state(current=0)
    results = refresh_recharge_resources(state, FixedDiceProvider([5]))
    events, sequence = build_recharge_events(state, "monster-1", 2, 7, results)
    assert sequence == 8 and len(events) == 1
    event = events[0]
    assert event.sequence == 7 and event.feature_id == "breath"
    assert event.resource_remaining == 1
    assert "d6: 5 vs 5+" in event.description and "recharged to 1" in event.description
    assert event.audit is not None
    assert [step.phase for step in event.audit.steps] == [AuditPhase.ROLL, AuditPhase.RESOURCE_CHANGE]


def test_non_recharge_limited_resource_never_rolls_at_turn_start() -> None:
    state = _state(current=0, recharge_minimum=None)
    # FixedDiceProvider intentionally requires at least one queued roll. A sentinel
    # roll is safe here: if non-Recharge resources ever consume it, this test's
    # empty result/state assertions fail and expose the lifecycle regression.
    assert refresh_recharge_resources(state, FixedDiceProvider([6])) == []
    assert state.resources[0].current_uses == 0
