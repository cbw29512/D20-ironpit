from __future__ import annotations

import pytest

from app.combat.legendary_actions import can_spend_legendary_action, spend_legendary_action
from app.combat.state import begin_turn, build_combatant_state
from app.content.roster import build_arena_roster
from app.domain.legendary_actions import LegendaryActionOption, LegendaryActionPool


def _state():
    wolf = next(monster for monster in build_arena_roster().monsters if monster.name == "Wolf")
    template = wolf.model_copy(update={
        "legendary_actions": LegendaryActionPool(
            max_uses=3,
            options=[
                LegendaryActionOption(
                    id="pounce",
                    name="Pounce",
                    kind="attack",
                    action_id="bite",
                ),
                LegendaryActionOption(
                    id="gaze",
                    name="Gaze",
                    kind="saving_throw",
                    action_id="gaze",
                    once_until_owner_turn=True,
                ),
            ],
        )
    })
    return build_combatant_state(template)


def test_pool_starts_full_and_only_works_after_another_creatures_turn() -> None:
    state = _state()
    assert state.legendary_action_uses_remaining == 3
    assert not can_spend_legendary_action(
        state, "pounce", owner_combatant_id="wolf-1", completed_turn_combatant_id="wolf-1"
    )
    assert can_spend_legendary_action(
        state, "pounce", owner_combatant_id="wolf-1", completed_turn_combatant_id="hero-1"
    )


def test_spend_lockout_and_owner_turn_refresh() -> None:
    state = _state()
    spend_legendary_action(state, "gaze")
    assert state.legendary_action_uses_remaining == 2
    assert state.legendary_action_locked_option_ids == ["gaze"]
    assert not can_spend_legendary_action(
        state, "gaze", owner_combatant_id="wolf-1", completed_turn_combatant_id="hero-1"
    )
    begin_turn(state)
    assert state.legendary_action_uses_remaining == 3
    assert state.legendary_action_locked_option_ids == []


def test_spend_fails_closed_when_pool_is_exhausted() -> None:
    state = _state()
    spend_legendary_action(state, "pounce")
    spend_legendary_action(state, "pounce")
    spend_legendary_action(state, "pounce")
    assert not can_spend_legendary_action(
        state, "pounce", owner_combatant_id="wolf-1", completed_turn_combatant_id="hero-1"
    )
    with pytest.raises(ValueError, match="Insufficient legendary action uses"):
        spend_legendary_action(state, "pounce")
