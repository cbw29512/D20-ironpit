"""Cross-target single-roll invariant for declarative typed save damage."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.combat.save_targets import resolve_save_targets
from app.domain.models import SavingThrowAction
from app.domain.save_damage import SaveDamageComponent


class ScriptedDice:
    def __init__(self, values: list[tuple[int, int]]) -> None:
        self.values = iter(values)
        self.calls: list[int] = []

    def roll(self, sides: int) -> int:
        expected, result = next(self.values)
        assert sides == expected
        self.calls.append(sides)
        return result


def _resolve_and_capture(action: SavingThrowAction, dice: ScriptedDice):
    actor = SimpleNamespace(combatant_id="actor", state=SimpleNamespace())
    targets = [SimpleNamespace(combatant_id="one"), SimpleNamespace(combatant_id="two")]
    setup = SimpleNamespace(heroes=[], monsters=[])
    captures: list[object] = []

    def fake_chain(sequence, round_number, actor, target, action, distance, dice, setup, **kwargs):
        captures.append(kwargs["shared_damage_rolls"])
        return [SimpleNamespace(target_id=target.combatant_id)], sequence + 1

    with (
        patch("app.combat.save_targets.validate_save_targets", return_value=targets),
        patch("app.combat.save_targets.action_resource_available", return_value=True),
        patch("app.combat.save_targets.spend_action_resource", return_value=None),
        patch("app.combat.save_targets.resolve_save_event_chain", side_effect=fake_chain),
    ):
        events, next_sequence = resolve_save_targets(
            1, 1, actor, setup, action, ("one", "two"),
            dice, skip_range_check=True,
        )
    assert len(events) == 2
    assert next_sequence == 3
    return captures


def test_typed_component_save_rolls_once_for_both_targets() -> None:
    action = SavingThrowAction(
        id="two-types", name="Two Types", save_ability="dexterity", dc=16, range_ft=15,
        damage_components=[
            SaveDamageComponent(dice_count=1, dice_size=6, damage_type="bludgeoning"),
            SaveDamageComponent(dice_count=1, dice_size=8, damage_type="slashing"),
        ],
        success_damage="half",
    )
    dice = ScriptedDice([(6, 6), (8, 8)])
    assert _resolve_and_capture(action, dice) == [
        [[6], [8]], [[6], [8]],
    ]
    assert dice.calls == [6, 8]


@pytest.mark.parametrize("damage_dice_count", [0, 2])
def test_legacy_and_non_damage_multi_target_actions_preserve_shared_rolls(
    damage_dice_count: int,
) -> None:
    action = SavingThrowAction(
        id="legacy", name="Legacy", save_ability="constitution", dc=12, range_ft=30,
        damage_dice_count=damage_dice_count,
        damage_dice_size=6, damage_type="fire" if damage_dice_count else None,
    )
    dice = ScriptedDice([(6, 6), (6, 3)] if damage_dice_count else [])
    expected = [6, 3] if damage_dice_count else None
    assert _resolve_and_capture(action, dice) == [expected, expected]
    assert dice.calls == [6] * damage_dice_count
