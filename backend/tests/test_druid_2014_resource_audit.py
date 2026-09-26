from __future__ import annotations

from app.content.character_resource_audit import expected_resources, expected_unlimited_resources
from app.content.druid_land_2014_profile import build_thalen_greenbough_2014_profile


def test_2014_druid_resource_oracle_covers_spell_slots_and_wild_shape() -> None:
    one = build_thalen_greenbough_2014_profile(1)
    two = build_thalen_greenbough_2014_profile(2)
    twenty = build_thalen_greenbough_2014_profile(20)

    assert expected_resources(one) == {"spell-slot-1": 2}
    assert expected_resources(two) == {"wild-shape": 2, "spell-slot-1": 3}
    assert expected_resources(twenty)["spell-slot-9"] == 1
    assert "wild-shape" not in expected_resources(twenty)
    assert expected_unlimited_resources(twenty) == ("wild-shape",)
