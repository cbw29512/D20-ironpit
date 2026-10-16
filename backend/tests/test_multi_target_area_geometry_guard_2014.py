"""Direct multi-target saves must honor source geometry, target uniqueness and shared rolls."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.combat.multi_target_save_actions import (
    choose_multi_target_save_action,
    resolve_multi_target_save_action,
)
from app.domain.models import SavingThrowAction
from app.domain.save_damage import SaveDamageComponent


def _action(*, area=False, typed=False):
    return SavingThrowAction(
        id="source-neutral", name="Renamed Homebrew Action",
        save_ability="dexterity", dc=15, range_ft=30, max_targets=2,
        area={"shape": "cone", "origin": "self", "length_ft": 15} if area else None,
        damage_components=[
            SaveDamageComponent(dice_count=1, dice_size=6, damage_type="bludgeoning"),
            SaveDamageComponent(dice_count=1, dice_size=8, damage_type="slashing"),
        ] if typed else [],
    )


def _targets():
    return (SimpleNamespace(combatant_id="one"), SimpleNamespace(combatant_id="two"))


def test_area_action_not_selected_by_direct_provider():
    actor = SimpleNamespace(
        combatant_id="caster",
        state=SimpleNamespace(template=SimpleNamespace(saving_throw_actions=[_action(area=True)])),
    )
    with (
        patch("app.combat.multi_target_save_actions.is_available", return_value=True),
        patch("app.combat.multi_target_save_actions.target_order") as order,
    ):
        assert choose_multi_target_save_action(actor, SimpleNamespace()) is None
        order.assert_not_called()


@pytest.mark.parametrize("selection, expected", [
    (lambda: (_action(area=True), _targets()), "geometry-validated placement"),
    (lambda: (_action(), (_targets()[0], _targets()[0])), "unique target IDs"),
])
def test_invalid_selection_fails_before_spending(selection, expected):
    actor = SimpleNamespace(combatant_id="caster", state=SimpleNamespace())
    with (
        patch("app.combat.multi_target_save_actions.spend") as spend,
        patch("app.combat.multi_target_save_actions.spend_action_resource") as resource,
        patch("app.combat.multi_target_save_actions.resolve_save_event_chain") as resolve,
    ):
        with pytest.raises(ValueError, match=expected):
            resolve_multi_target_save_action(
                1, 1, actor, SimpleNamespace(), SimpleNamespace(), selection(),
            )
        spend.assert_not_called()
        resource.assert_not_called()
        resolve.assert_not_called()


def test_typed_components_roll_once_for_all_direct_targets():
    actor = SimpleNamespace(combatant_id="caster", state=SimpleNamespace())
    action = _action(typed=True)
    rolls = iter([(6, 4), (8, 7)])
    calls = []
    captured = []

    def roll(sides):
        expected, value = next(rolls)
        assert sides == expected
        calls.append(sides)
        return value

    def chain(sequence, round_number, actor, target, action, distance, dice, setup, **kwargs):
        captured.append(kwargs["shared_damage_rolls"])
        return [SimpleNamespace(target_id=target.combatant_id)], sequence + 1

    with (
        patch("app.combat.multi_target_save_actions.is_available", return_value=True),
        patch("app.combat.multi_target_save_actions.action_resource_available", return_value=True),
        patch("app.combat.multi_target_save_actions.spend_action_resource", return_value=None),
        patch("app.combat.multi_target_save_actions.spend"),
        patch("app.combat.multi_target_save_actions.combatant_distance", return_value=5),
        patch("app.combat.multi_target_save_actions.legal_save_action", return_value=True),
        patch("app.combat.multi_target_save_actions.resolve_save_event_chain", side_effect=chain),
    ):
        events, sequence = resolve_multi_target_save_action(
            1, 1, actor, SimpleNamespace(heroes=[], monsters=[]),
            SimpleNamespace(roll=roll), (action, _targets()),
        )
    assert len(events) == 2 and sequence == 3
    assert calls == [6, 8]
    assert captured == [[[4], [7]], [[4], [7]]]
