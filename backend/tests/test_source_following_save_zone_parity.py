"""Regression contracts for universal moving save zones and source-owned timing."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from pydantic import ValidationError

from app.combat import persistent_save_zone_resolution as resolver
from app.combat.persistent_save_zone_geometry import member_in_save_zone
from app.domain.grid import GridPosition
from app.domain.persistent_save_zones import PersistentSaveZoneAction, PersistentSaveZoneState
from app.domain.size import CreatureSize


def action(**overrides):
    data = dict(id="zone", name="Moving Cloud", level=0, cast_range_ft=0,
                center_on_source=True, radius_ft=10, duration_rounds=10,
                save_ability="constitution", dc=11, triggers=["start_turn"],
                failed_save_condition_id="poisoned")
    data.update(overrides)
    return PersistentSaveZoneAction(**data)


def zone(**overrides):
    data = dict(zone_id="zone", source_id="source", source_side="heroes",
                action_id="zone", action_name="Moving Cloud",
                position=GridPosition(x=1, y=7), radius_ft=10,
                expires_round=11, save_ability="constitution", dc=11,
                triggers=["start_turn"], target_policy="all",
                failed_save_condition_id="poisoned")
    data.update(overrides)
    return PersistentSaveZoneState(**data)


def member(name, x):
    return NS(combatant_id=name, side="heroes" if name == "source" else "monsters",
              state=NS(position=GridPosition(x=x, y=7), current_hp=10,
                       is_alive=True, is_dead=False,
                       template=NS(name=name, size=CreatureSize.MEDIUM)))


def test_following_is_opt_in_and_requires_source_centering():
    assert not action().follows_source
    assert action(follows_source=True).follows_source
    with pytest.raises(ValidationError, match="must start at their source"):
        action(follows_source=True, center_on_source=False)


def test_moving_zone_uses_live_source_position_and_fails_closed():
    source, target = member("source", 5), member("target", 5)
    setup = NS(heroes=[source], monsters=[target])
    moving = zone(follows_source=True)
    assert member_in_save_zone(target, moving, setup)
    assert not member_in_save_zone(target, moving, None)
    source.state.position = GridPosition(x=1, y=7)
    assert not member_in_save_zone(target, moving, setup)
    assert not member_in_save_zone(target, moving, NS(heroes=[], monsters=[target]))
    assert not member_in_save_zone(target, zone(), setup)
    target.state.position = GridPosition(x=1, y=7)
    assert member_in_save_zone(target, zone(), setup)


def test_expiry_policy_passes_to_shared_condition_lifecycle(monkeypatch):
    source, target = member("source", 1), member("target", 1)
    setup = NS(heroes=[source], monsters=[target])
    observed = []
    monkeypatch.setattr(resolver, "resolve_saving_throw", lambda *_: (None, False))

    def apply(_state, effect, _source, **options):
        observed.append(options)
        return effect

    monkeypatch.setattr(resolver, "apply_timed_condition", apply)
    events, _ = resolver.resolve_save_zone_trigger(
        1, 1, target, setup,
        zone(follows_source=True, failed_save_expiry_timing="target_turn_start"),
        None, "turn:target", "start_turn",
    )
    assert events[0].applied_condition_ids == ["poisoned"]
    assert observed[0]["expiry_timing"] == "target_turn_start"
    assert observed[0]["expires_at_start_of_source_turn"] is False


def test_browser_serializer_emits_only_nondefault_moving_policy():
    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from browser_template_serializer import _save_zone
    assert "followsSource" not in _save_zone(action())
    assert "failedSaveExpiryTiming" not in _save_zone(action())
    row = _save_zone(action(follows_source=True,
                            failed_save_expiry_timing="target_turn_start"))
    assert row["followsSource"] is True
    assert row["failedSaveExpiryTiming"] == "target_turn_start"


def test_dretch_source_action_declares_following_and_start_of_turn_expiry():
    from app.content.monster_fetid_cloud_2014 import fetid_cloud_zone_2014
    from app.content.monster_source_2014 import load_monster_source_2014

    dretch = next(row for row in load_monster_source_2014() if row.id == "dretch")
    original = dretch.model_dump_json()
    effect = fetid_cloud_zone_2014(dretch)
    assert effect is not None
    assert effect.follows_source
    assert effect.failed_save_expiry_timing == "target_turn_start"
    assert effect.target_policy == "all"
    assert dretch.model_dump_json() == original
