from __future__ import annotations

from app.content.druid_2014_progression import DRUID_2014_LEVELS, druid_2014_features


def test_2014_druid_progression_is_contiguous_and_slot_correct() -> None:
    assert tuple(DRUID_2014_LEVELS) == tuple(range(1, 21))
    assert DRUID_2014_LEVELS[1].spell_slots == (2, 0, 0, 0, 0, 0, 0, 0, 0)
    assert DRUID_2014_LEVELS[5].spell_slots == (4, 3, 2, 0, 0, 0, 0, 0, 0)
    assert DRUID_2014_LEVELS[11].spell_slots == (4, 3, 3, 3, 2, 1, 0, 0, 0)
    assert DRUID_2014_LEVELS[17].spell_slots == (4, 3, 3, 3, 2, 1, 1, 1, 1)
    assert DRUID_2014_LEVELS[20].spell_slots == (4, 3, 3, 3, 3, 2, 2, 1, 1)


def test_2014_druid_wild_shape_breakpoints_are_explicit() -> None:
    assert DRUID_2014_LEVELS[1].wild_shape_uses == 0
    assert DRUID_2014_LEVELS[2].max_wild_shape_cr == "1/4"
    assert DRUID_2014_LEVELS[4].max_wild_shape_cr == "1/2"
    assert DRUID_2014_LEVELS[4].wild_shape_swim is True
    assert DRUID_2014_LEVELS[8].max_wild_shape_cr == "1"
    assert DRUID_2014_LEVELS[8].wild_shape_fly is True
    assert DRUID_2014_LEVELS[20].wild_shape_unlimited is True


def test_2014_druid_feature_breakpoints_are_persistent() -> None:
    level_twenty = set(druid_2014_features(20))
    assert {
        "spellcasting", "wild-shape", "druid-circle",
        "timeless-body", "beast-spells", "archdruid",
    } <= level_twenty
