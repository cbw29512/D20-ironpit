"""Direct multi-target saves cannot bypass area geometry or hit a repeated ID."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.combat.multi_target_save_actions import (
    choose_multi_target_save_action,
    resolve_multi_target_save_action,
)
from app.domain.models import SavingThrowAction


def _area_action() -> SavingThrowAction:
    return SavingThrowAction(
        id="synthetic-area", name="Renamed Homebrew Area",
        save_ability="dexterity", dc=15, range_ft=30, max_targets=2,
        area={"shape": "cone", "origin": "self", "length_ft": 15},
    )


def test_area_action_is_not_chosen_by_direct_multi_target_provider() -> None:
    actor = SimpleNamespace(
        combatant_id="source",
        state=SimpleNamespace(template=SimpleNamespace(saving_throw_actions=[_area_action()])),
    )
    with (
        patch("app.combat.multi_target_save_actions.is_available", return_value=True),
        patch("app.combat.multi_target_save_actions.target_order") as order,
    ):
        assert choose_multi_target_save_action(actor, SimpleNamespace()) is None
        order.assert_not_called()


def test_area_action_cannot_bypass_placement_or_spend() -> None:
    actor = SimpleNamespace(combatant_id="source", state=SimpleNamespace())
    targets = (SimpleNamespace(combatant_id="one"), SimpleNamespace(combatant_id="two"))
    with (
        patch("app.combat.multi_target_save_actions.spend") as spend,
        patch("app.combat.multi_target_save_actions.spend_action_resource") as resource,
        patch("app.combat.multi_target_save_actions.resolve_save_event_chain") as resolve,
    ):
        with pytest.raises(ValueError, match="geometry-validated placement"):
            resolve_multi_target_save_action(
                1, 1, actor, SimpleNamespace(), SimpleNamespace(), (_area_action(), targets),
            )
        spend.assert_not_called()
        resource.assert_not_called()
        resolve.assert_not_called()


def test_duplicate_target_ids_cannot_spend_or_resolve() -> None:
    actor = SimpleNamespace(combatant_id="source", state=SimpleNamespace())
    repeated = SimpleNamespace(combatant_id="same-target")
    action = _area_action().model_copy(update={"area": None})
    with (
        patch("app.combat.multi_target_save_actions.spend") as spend,
        patch("app.combat.multi_target_save_actions.spend_action_resource") as resource,
        patch("app.combat.multi_target_save_actions.resolve_save_event_chain") as resolve,
    ):
        with pytest.raises(ValueError, match="unique target IDs"):
            resolve_multi_target_save_action(
                1, 1, actor, SimpleNamespace(), SimpleNamespace(),
                (action, (repeated, repeated)),
            )
        spend.assert_not_called()
        resource.assert_not_called()
        resolve.assert_not_called()


def test_typed_damage_is_rolled_once_and_reused_for_direct_targets() -> None:
    """Both targets save separately against identical component dice."""
    actor = SimpleNamespace(combatant_id="source", state=SimpleNamespace())
    targets = (
        SimpleNamespace(combatant_id="one", state=SimpleNamespace()),
        SimpleNamespace(combatant_id="two", state=SimpleNamespace()),
    )
    setup = SimpleNamespace(heroes=list(targets), monsters=[actor])
    action = SavingThrowAction(
        id="synthetic-components", name="Renamed Two-Type Effect",
        save_ability="dexterity", dc=15, range_ft=30, max_targets=2,
        damage_components=[
            {"dice_count": 1, "dice_size": 6, "damage_type": "bludgeoning"},
            {"dice_count": 1, "dice_size": 8, "damage_type": "slashing"},
        ],
    )
    rolled: list[int] = []
    seen: list[list[list[int]]] = []

    def roll(sides: int) -> int:
        rolled.append(sides)
        return sides

    def resolve(sequence, _round, _actor, _target, _action, _distance, _dice, _setup, **kwargs):
        seen.append(kwargs["shared_damage_rolls"])
        return [SimpleNamespace(sequence=sequence)], sequence + 1

    with (
        patch("app.combat.multi_target_save_actions.is_available", return_value=True),
        patch("app.combat.multi_target_save_actions.action_resource_available", return_value=True),
        patch("app.combat.multi_target_save_actions.legal_save_action", return_value=True),
        patch("app.combat.multi_target_save_actions.combatant_distance", return_value=5),
        patch("app.combat.multi_target_save_actions.spend_action_resource", return_value=None),
        patch("app.combat.multi_target_save_actions.spend") as spend,
        patch("app.combat.multi_target_save_actions.resolve_save_event_chain", side_effect=resolve),
    ):
        events, next_sequence = resolve_multi_target_save_action(
            1, 1, actor, setup, SimpleNamespace(roll=roll), (action, targets),
        )
    assert len(events) == 2
    assert next_sequence == 3
    assert rolled == [6, 8]
    assert seen == [[[6], [8]], [[6], [8]]]
    assert seen[0] is seen[1]
    spend.assert_called_once()
