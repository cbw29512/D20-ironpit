import pytest

from app.combat.general_actions import take_disengage
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior


def test_goblin_nimble_escape_grants_bonus_action_disengage() -> None:
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")

    event = take_disengage(
        1,
        1,
        goblin,
        action_cost="bonus_action",
        feature_id="nimble-escape-disengage",
    )

    assert event.event_type == "disengage"
    assert event.feature_id == "nimble-escape-disengage"
    assert goblin.bonus_action_available is False
    assert goblin.action_available is True
    assert goblin.disengaged_this_turn is True


def test_bonus_action_disengage_requires_verified_grant() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")

    with pytest.raises(ValueError, match="not granted"):
        take_disengage(
            1,
            1,
            fighter,
            action_cost="bonus_action",
            feature_id="nimble-escape-disengage",
        )

    assert fighter.bonus_action_available is True
    assert fighter.action_available is True


def test_nimble_escape_does_not_replace_normal_action_disengage() -> None:
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")

    take_disengage(1, 1, goblin)

    assert goblin.action_available is False
    assert goblin.bonus_action_available is True
    assert goblin.disengaged_this_turn is True
