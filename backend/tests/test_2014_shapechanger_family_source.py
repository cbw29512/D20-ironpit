"""Permanent regressions for the shared 2014 Shapechanger source contract."""
from __future__ import annotations

import pytest

from app.content.monster_source_2014 import load_source_monster_2014
from app.content.monster_source_shapechanger_2014 import (
    SHAPECHANGER_FAMILY_2014,
    source_proven_shapechanger_2014,
)


@pytest.mark.parametrize("monster_id", sorted(SHAPECHANGER_FAMILY_2014))
def test_shapechanger_family_source_proven(monster_id: str) -> None:
    monster = load_source_monster_2014(monster_id)
    proven = source_proven_shapechanger_2014(monster)
    assert proven is not None, monster_id
    assert proven["source_id"] == "shapechanger"
    assert proven["action_cost"] == "action"
    assert proven["ends_on_death"] is True
    assert proven["stats_identical_except_size"] is True
    assert proven["equipment_preserved"] is True


def test_shapechanger_fails_closed_on_mutation() -> None:
    monster = load_source_monster_2014("imp")
    original = monster.source_traits
    monster.source_traits = original.replace("reverts to its true form if it dies", "does not revert")
    assert source_proven_shapechanger_2014(monster) is None


def test_non_shapechanger_rejected() -> None:
    monster = load_source_monster_2014("frog")
    assert source_proven_shapechanger_2014(monster) is None
