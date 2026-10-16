"""Source-card target limits reject invalid saves before any fight mutation."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.combat.save_targets import resolve_save_targets, validate_save_targets
from app.domain.models import SavingThrowAction


def _action(cap: int) -> SavingThrowAction:
    return SavingThrowAction(
        id="synthetic-save", name="Renamed Homebrew Action",
        save_ability="dexterity", dc=16, range_ft=30, max_targets=cap,
    )


@pytest.mark.parametrize("cap, selected", [
    (1, ("hero:one", "hero:two")),
    (2, ("hero:one", "hero:two", "hero:three")),
])
def test_excess_targets_fail_before_resource_or_dice_use(cap: int, selected: tuple[str, ...]) -> None:
    actor = SimpleNamespace(combatant_id="monster:source", side="monsters", state=SimpleNamespace())
    setup = SimpleNamespace(heroes=[], monsters=[])
    with (
        patch("app.combat.save_targets.action_resource_available") as available,
        patch("app.combat.save_targets.spend_action_resource") as spend,
        patch("app.combat.save_targets.resolve_save_event_chain") as resolve,
    ):
        with pytest.raises(ValueError, match="target cap"):
            resolve_save_targets(1, 1, actor, setup, _action(cap), selected, SimpleNamespace())
        available.assert_not_called()
        spend.assert_not_called()
        resolve.assert_not_called()


def test_exact_source_cap_allows_legal_targets_without_name_dispatch() -> None:
    actor = SimpleNamespace(combatant_id="monster:source", side="monsters")
    state = SimpleNamespace(is_alive=True, is_dead=False, current_hp=12)
    targets = [
        SimpleNamespace(combatant_id=f"hero:{number}", side="heroes", state=state)
        for number in (1, 2)
    ]
    setup = SimpleNamespace(heroes=targets, monsters=[])
    with patch("app.combat.save_targets.legal_save_action", return_value=True):
        selected = validate_save_targets(
            actor, setup, _action(2), ("hero:1", "hero:2"), skip_range_check=True,
        )
    assert selected == targets

def test_area_saves_use_geometry_not_single_target_default() -> None:
    """Area geometry may legitimately select several targets with default max_targets=1."""
    actor = SimpleNamespace(combatant_id="monster:source", side="monsters")
    state = SimpleNamespace(is_alive=True, is_dead=False, current_hp=12)
    targets = [
        SimpleNamespace(combatant_id=f"hero:{number}", side="heroes", state=state)
        for number in (1, 2)
    ]
    setup = SimpleNamespace(heroes=targets, monsters=[])
    action = _action(1).model_copy(update={"area": {"shape": "cone", "origin": "self", "length_ft": 15}})
    with patch("app.combat.save_targets.legal_save_action", return_value=True):
        selected = validate_save_targets(
            actor, setup, action, ("hero:1", "hero:2"), skip_range_check=True,
        )
    assert selected == targets
