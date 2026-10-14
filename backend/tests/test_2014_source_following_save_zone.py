from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.combat.persistent_save_zone_geometry import member_in_save_zone
from app.domain.grid import GridPosition
from app.domain.size import CreatureSize


def _member(identifier: str, x: int):
    state = SimpleNamespace(
        position=GridPosition(x=x, y=0),
        template=SimpleNamespace(size=CreatureSize.MEDIUM),
    )
    return SimpleNamespace(combatant_id=identifier, state=state)


def test_source_following_zone_moves_with_source() -> None:
    source = _member("source", 0)
    target = _member("target", 2)
    setup = SimpleNamespace(heroes=[target], monsters=[source])
    zone = SimpleNamespace(
        position=GridPosition(x=0, y=0),
        radius_ft=5,
        follows_source=True,
        source_id="source",
    )
    assert not member_in_save_zone(target, zone, setup)
    source.state.position = GridPosition(x=1, y=0)
    assert member_in_save_zone(target, zone, setup)


def test_stationary_zone_does_not_follow_source() -> None:
    source = _member("source", 0)
    target = _member("target", 2)
    setup = SimpleNamespace(heroes=[target], monsters=[source])
    zone = SimpleNamespace(
        position=GridPosition(x=0, y=0),
        radius_ft=5,
        follows_source=False,
        source_id="source",
    )
    source.state.position = GridPosition(x=1, y=0)
    assert not member_in_save_zone(target, zone, setup)


def test_following_zone_requires_encounter_and_known_source() -> None:
    target = _member("target", 1)
    zone = SimpleNamespace(
        position=GridPosition(x=0, y=0),
        radius_ft=5,
        follows_source=True,
        source_id="missing",
    )
    with pytest.raises(ValueError, match="encounter state"):
        member_in_save_zone(target, zone)
    assert not member_in_save_zone(
        target, zone, SimpleNamespace(heroes=[target], monsters=[]),
    )
