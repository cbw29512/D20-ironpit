"""Source-owned save-zone policy parity, without monster-name dispatch."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from pydantic import ValidationError

from app.combat import persistent_save_zone_resolution as zone_runtime
from app.domain.grid import GridPosition
from app.domain.persistent_save_zones import PersistentSaveZoneAction, PersistentSaveZoneState


def _action(**changes):
    source = dict(
        id="cloud", name="Any Cloud", level=0, cast_range_ft=0,
        radius_ft=10, duration_rounds=10, save_ability="constitution",
        dc=11, triggers=["start_turn"], failed_save_condition_id="poisoned",
    )
    source.update(changes)
    return PersistentSaveZoneAction(**source)


def _zone(**changes):
    state = dict(
        zone_id="zone", source_id="source", source_side="heroes",
        action_id="cloud", action_name="Any Cloud",
        position=GridPosition(x=1, y=7), radius_ft=10,
        expires_round=11, save_ability="constitution", dc=11,
        triggers=["start_turn"], failed_save_condition_id="poisoned",
    )
    state.update(changes)
    return PersistentSaveZoneState(**state)


def _member(identifier, side):
    return NS(
        combatant_id=identifier, side=side,
        state=NS(is_alive=True, is_dead=False, current_hp=10,
                 template=NS(name=identifier), position=GridPosition(x=1, y=7)),
    )


def test_opt_in_policy_validation_and_browser_serialization():
    assert _action().target_policy == "enemies"
    assert _action().save_context == "spell"
    assert not _action().failed_save_suppress_reactions
    assert not _action().failed_save_action_bonus_exclusive
    with pytest.raises(ValidationError):
        _action(target_policy="unknown")
    with pytest.raises(ValidationError):
        _action(save_context="unknown")

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from browser_template_serializer import _save_zone
    assert "targetPolicy" not in _save_zone(_action())
    assert "saveContext" not in _save_zone(_action())
    assert "failedSaveSuppressReactions" not in _save_zone(_action())
    assert "failedSaveActionBonusExclusive" not in _save_zone(_action())
    values = _save_zone(_action(target_policy="all", save_context="nonmagical"))
    assert values["targetPolicy"] == "all"
    assert values["saveContext"] == "nonmagical"
    assert _save_zone(_action(failed_save_suppress_reactions=True))["failedSaveSuppressReactions"] is True
    assert _save_zone(_action(failed_save_action_bonus_exclusive=True))["failedSaveActionBonusExclusive"] is True


@pytest.mark.parametrize("policy,expected", [
    ("enemies", ["enemy"]), ("all", ["source", "ally", "enemy"]),
])
def test_source_configured_targets_and_nonmagical_save_context(
    monkeypatch, policy, expected,
):
    # Use the real zone schema and resolver; stub geometry and die outcome only.
    monkeypatch.setattr(zone_runtime, "member_in_save_zone", lambda *_: True)
    contexts = []

    def save(_state, _ability, _dc, _dice, context):
        contexts.append((context.magical_effect, context.spell_effect))
        return None, True

    monkeypatch.setattr(zone_runtime, "resolve_saving_throw", save)
    zone = _zone(target_policy=policy, save_context="nonmagical")
    seen = []
    for identifier, side in [
        ("source", "heroes"), ("ally", "heroes"), ("enemy", "monsters"),
    ]:
        actor = _member(identifier, side)
        events, _ = zone_runtime.resolve_save_zone_trigger(
            1, 1, actor, None, zone, None, f"turn:{identifier}", "start_turn",
        )
        if events:
            seen.append(identifier)
    assert seen == expected
    assert contexts == [(False, False)] * len(expected)


def test_failed_nonmagical_save_transfers_provenance_to_condition(monkeypatch):
    monkeypatch.setattr(zone_runtime, "member_in_save_zone", lambda *_: True)
    monkeypatch.setattr(
        zone_runtime, "resolve_saving_throw", lambda *_: (None, False),
    )
    observed = []

    def apply(_state, effect, source, **options):
        observed.append((effect, source, options))
        return effect

    monkeypatch.setattr(zone_runtime, "apply_timed_condition", apply)
    actor = _member("ally", "heroes")
    zone = _zone(
        target_policy="all", save_context="nonmagical",
        failed_save_suppress_reactions=True, failed_save_action_bonus_exclusive=True,
    )
    events, _ = zone_runtime.resolve_save_zone_trigger(
        1, 1, actor, None, zone, None, "turn:ally", "start_turn",
    )
    assert events[0].applied_condition_ids == ["poisoned"]
    assert observed[0][2]["source_is_magical"] is False
    assert observed[0][2]["expires_at_start_of_source_turn"] is False
    assert observed[0][2]["suppress_reactions"] is True
    assert observed[0][2]["control_limits"].action_bonus_exclusive is True
