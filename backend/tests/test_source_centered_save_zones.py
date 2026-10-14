from __future__ import annotations

from app.domain.persistent_save_zones import PersistentSaveZoneAction


def test_source_centered_save_zone_is_explicit_and_opt_in() -> None:
    base = dict(
        id="source-cloud", name="Source Cloud", level=0, cast_range_ft=0,
        radius_ft=10, duration_rounds=10, save_ability="constitution",
        dc=11, triggers=["start_turn"], failed_save_condition_id="poisoned",
    )
    assert PersistentSaveZoneAction(**base).center_on_source is False
    action = PersistentSaveZoneAction(**base, center_on_source=True)
    assert action.center_on_source
    assert action.model_dump()["center_on_source"] is True
