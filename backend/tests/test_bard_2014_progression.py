from __future__ import annotations

import pytest

from app.content.bard_2014_progression import BARD_2014_LEVELS, bard_2014_features, bard_2014_level
from app.content.bard_lore_2014_progression import lore_bard_2014_features


def test_2014_bard_progression_covers_every_level_once() -> None:
    assert tuple(BARD_2014_LEVELS) == tuple(range(1, 21))


@pytest.mark.parametrize(
    ("level", "pb", "cantrips", "spells", "die", "slots"),
    [
        (1, 2, 2, 4, 6, (2, 0, 0, 0, 0, 0, 0, 0, 0)),
        (5, 3, 3, 8, 8, (4, 3, 2, 0, 0, 0, 0, 0, 0)),
        (10, 4, 4, 14, 10, (4, 3, 3, 3, 2, 0, 0, 0, 0)),
        (15, 5, 4, 19, 12, (4, 3, 3, 3, 2, 1, 1, 1, 0)),
        (20, 6, 4, 22, 12, (4, 3, 3, 3, 3, 2, 2, 1, 1)),
    ],
)
def test_2014_bard_table_matches_basic_rules(
    level: int,
    pb: int,
    cantrips: int,
    spells: int,
    die: int,
    slots: tuple[int, ...],
) -> None:
    row = bard_2014_level(level)
    assert row.proficiency_bonus == pb
    assert row.cantrips_known == cantrips
    assert row.spells_known == spells
    assert row.bardic_inspiration_die == die
    assert row.spell_slots == slots


def test_2014_bard_features_are_persistent_level_deltas() -> None:
    assert bard_2014_features(1) == ("bardic-inspiration", "spellcasting")
    assert {"jack-of-all-trades", "song-of-rest-d6"} <= set(bard_2014_features(2))
    assert {"font-of-inspiration", "countercharm"} <= set(bard_2014_features(6))
    assert {"magical-secrets", "magical-secrets-2", "magical-secrets-3"} <= set(bard_2014_features(18))
    assert "superior-inspiration" in bard_2014_features(20)


def test_2014_lore_features_land_only_at_subclass_levels() -> None:
    assert lore_bard_2014_features(2) == ()
    assert lore_bard_2014_features(3) == ("cutting-words",)
    assert lore_bard_2014_features(6) == ("cutting-words", "additional-magical-secrets")
    assert lore_bard_2014_features(14) == (
        "cutting-words",
        "additional-magical-secrets",
        "peerless-skill",
    )


@pytest.mark.parametrize("level", [0, 21])
def test_2014_bard_progression_rejects_out_of_range_levels(level: int) -> None:
    with pytest.raises(ValueError):
        bard_2014_level(level)
    with pytest.raises(ValueError):
        lore_bard_2014_features(level)
