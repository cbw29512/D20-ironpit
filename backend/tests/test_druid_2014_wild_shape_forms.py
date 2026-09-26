from __future__ import annotations

from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_form_2014


def test_land_druid_canonical_wild_shape_breakpoints() -> None:
    assert canonical_wild_shape_form_2014(2).monster_id == "2014-wolf"
    assert canonical_wild_shape_form_2014(3).monster_id == "2014-wolf"
    assert canonical_wild_shape_form_2014(4).monster_id == "2014-crocodile"
    assert canonical_wild_shape_form_2014(7).monster_id == "2014-crocodile"
    assert canonical_wild_shape_form_2014(8).monster_id == "2014-brown-bear"
    assert canonical_wild_shape_form_2014(20).monster_id == "2014-brown-bear"


def test_land_druid_form_crs_match_locked_policy() -> None:
    assert canonical_wild_shape_form_2014(2).challenge_rating == "1/4"
    assert canonical_wild_shape_form_2014(4).challenge_rating == "1/2"
    assert canonical_wild_shape_form_2014(8).challenge_rating == "1"
