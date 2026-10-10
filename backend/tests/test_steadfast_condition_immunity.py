"""Steadfast never grants unconditional or out-of-range immunity."""
from types import SimpleNamespace
from unittest.mock import patch

from app.combat.steadfast_condition_immunity import steadfast_frightened_immunity


def _actor(*, traits=("Steadfast",), ruleset="2014"):
    return SimpleNamespace(state=SimpleNamespace(template=SimpleNamespace(
        ruleset=ruleset, source_trait_names=list(traits)
    )))


def test_steadfast_requires_printed_source_and_correct_condition():
    with patch("app.combat.steadfast_condition_immunity.has_visible_active_ally_within") as eligible:
        assert not steadfast_frightened_immunity(_actor(), None, "charmed")
        assert not steadfast_frightened_immunity(_actor(traits=()), None, "frightened")
        assert not steadfast_frightened_immunity(_actor(ruleset="2024"), None, "frightened")
        eligible.assert_not_called()


def test_steadfast_follows_live_ally_range_and_visibility():
    actor, setup = _actor(), object()
    with patch("app.combat.steadfast_condition_immunity.has_visible_active_ally_within") as eligible:
        eligible.return_value = True
        assert steadfast_frightened_immunity(actor, setup, "frightened")
        eligible.assert_called_once_with(actor, setup, 30)
        eligible.return_value = False
        assert not steadfast_frightened_immunity(actor, setup, "frightened")
