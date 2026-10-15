"""Regression contract: stationary save zones must not drift with their caster."""
from __future__ import annotations

from app.domain.grid import GridPosition
from app.domain.persistent_save_zones import PersistentSaveZoneState


def test_save_zone_position_is_fight_local_and_fixed_by_default() -> None:
    zone = PersistentSaveZoneState(
        zone_id="source:zone:1", source_id="source", source_side="monsters",
        action_id="generic-zone", action_name="Generic Zone",
        position=GridPosition(x=1, y=1), radius_ft=10, expires_round=3,
        save_ability="constitution", dc=11, triggers=["start_turn"],
        failed_save_condition_id="poisoned",
    )
    moved = zone.model_copy(deep=True)
    moved.position = GridPosition(x=2, y=1)
    assert zone.position == GridPosition(x=1, y=1)
    assert moved.position == GridPosition(x=2, y=1)
