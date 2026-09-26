from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.content.bard_2014_inspiration import build_bardic_inspiration_2014
from app.domain.d20_bonus_dice import D20BonusDieAction


@pytest.mark.parametrize(("level", "die"), [(1, 6), (5, 8), (10, 10), (15, 12), (20, 12)])
def test_bardic_inspiration_binds_level_scaled_die(level: int, die: int) -> None:
    action = build_bardic_inspiration_2014(level)
    assert action.action_cost == "bonus_action"
    assert action.range_ft == 60
    assert action.target_mode == "other_ally"
    assert action.resource_id == "bardic-inspiration"
    assert action.dice_size == die
    assert action.test_kinds == ["attack", "saving_throw", "ability_check"]
    assert action.duration_rounds == 100


def test_d20_bonus_action_rejects_duplicate_test_kinds() -> None:
    with pytest.raises(ValidationError):
        D20BonusDieAction(
            id="duplicate", name="Duplicate", action_cost="bonus_action", range_ft=30,
            resource_id="uses", dice_size=6, test_kinds=["attack", "attack"], duration_rounds=1,
        )


def test_self_targeted_d20_bonus_action_requires_zero_range() -> None:
    with pytest.raises(ValidationError):
        D20BonusDieAction(
            id="self", name="Self", action_cost="bonus_action", range_ft=30, target_mode="self",
            resource_id="uses", dice_size=6, test_kinds=["ability_check"], duration_rounds=1,
        )
