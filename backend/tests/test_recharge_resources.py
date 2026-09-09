from app.combat.dice import FixedDiceProvider
from app.combat.resources import recharge_start_events, recharge_start_of_turn
from app.combat.state import build_combatant_state
from app.content.roster import build_arena_roster
from app.domain.models import ResourceState


def _state_with_recharge(*, current_uses: int, minimum: int):
    template = build_arena_roster().monsters[0]
    state = build_combatant_state(template)
    state.resources = [
        ResourceState(
            id="test-recharge",
            name="Test Recharge",
            current_uses=current_uses,
            max_uses=1,
            recharge_d6_min=minimum,
        )
    ]
    return state


def test_recharge_5_6_rolls_only_when_depleted_and_restores_on_threshold() -> None:
    state = _state_with_recharge(current_uses=0, minimum=5)

    assert recharge_start_of_turn(state, FixedDiceProvider([4])) == [("test-recharge", 4, False)]
    assert state.resources[0].current_uses == 0

    assert recharge_start_of_turn(state, FixedDiceProvider([5])) == [("test-recharge", 5, True)]
    assert state.resources[0].current_uses == 1

    full_dice = FixedDiceProvider([1])
    assert recharge_start_of_turn(state, full_dice) == []
    assert full_dice.roll(6) == 1


def test_recharge_6_emits_audit_grade_start_turn_resource_event() -> None:
    state = _state_with_recharge(current_uses=0, minimum=6)

    events, next_sequence = recharge_start_events(
        sequence=7,
        round_number=3,
        state=state,
        actor_id="monster-1",
        dice=FixedDiceProvider([6]),
    )

    assert next_sequence == 8
    assert len(events) == 1
    event = events[0]
    assert event.sequence == 7
    assert event.round_number == 3
    assert event.feature_id == "recharge:test-recharge"
    assert event.attack_roll is not None
    assert event.attack_roll.total == 6
    assert event.resource_remaining == 1
    assert "needs 6" in event.description
    assert [step.kind for step in event.audit.steps] == ["roll", "resource"]
