"""A zero-HP save has no damage dice, but its target remains tactically valuable."""
from __future__ import annotations

from types import SimpleNamespace
import pytest

from app.combat.printed_damage import save_action_impact
from app.domain.actions import SavingThrowAction


def _target(hp: int):
    return SimpleNamespace(state=SimpleNamespace(current_hp=hp))


def test_direct_to_zero_save_uses_remaining_hp_as_rank_proxy():
    try:
        action = SavingThrowAction(
            id="unrelated", name="Any Save", range_ft=30,
            save_ability="wisdom", dc=11, failure_sets_zero_hp=True,
        )
        assert save_action_impact(action, _target(60)) == 60
        assert save_action_impact(action.model_copy(update={"name": "Other Name"}), _target(3)) == 3
    except Exception:
        raise


def test_damage_save_remains_original_mean_not_current_hp():
    try:
        action = SavingThrowAction(
            id="ordinary", name="Fire Save", range_ft=30, save_ability="dexterity",
            dc=11, damage_dice_count=2, damage_dice_size=6, damage_type="fire",
        )
        assert save_action_impact(action, _target(100)) == 7
    except Exception:
        raise


def test_unknown_remaining_hp_fails_closed_for_zero_hp_ranking():
    action = SavingThrowAction(
        id="invalid", name="Effect", range_ft=30, save_ability="wisdom",
        dc=11, failure_sets_zero_hp=True,
    )
    with pytest.raises(ValueError, match="valid current target HP"):
        save_action_impact(action, SimpleNamespace(state=SimpleNamespace(current_hp=-1)))
