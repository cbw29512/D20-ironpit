from __future__ import annotations

from pathlib import Path

from app.domain.persistent_save_zones import PersistentSaveZoneAction


def test_nonmagical_save_zone_is_declared_separately_from_spell() -> None:
    kwargs = dict(
        id="gas", name="Gas", level=0, cast_range_ft=0, radius_ft=10,
        duration_rounds=10, save_ability="constitution", dc=11,
        triggers=["start_turn"], failed_save_condition_id="poisoned",
    )
    assert PersistentSaveZoneAction(**kwargs).save_context == "spell"
    assert PersistentSaveZoneAction(**kwargs, save_context="nonmagical").save_context == "nonmagical"
