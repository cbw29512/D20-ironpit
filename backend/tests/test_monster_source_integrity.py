import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_integrity import (
    neighbor_name_bleed_issues,
    source_integrity_issues,
    validate_monster_source_integrity,
)


def test_corrected_srd_catalog_has_no_embedded_stat_blocks() -> None:
    rows = load_monster_rows()
    assert all(source_integrity_issues(row) == [] for row in rows)


def test_embedded_neighbor_stat_block_fails_closed() -> None:
    bad = {
        "name": "Snake",
        "traits": "",
        "actions": "Bite. Hit: 4. Crab Tiny Beast AC 11 Initiative +0 (10) HP 3 (1d4 + 1)",
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": (
            "AC 13 Initiative +2 (12) HP 13. Actions Bite. "
            "Crab Tiny Beast AC 11 Initiative +0 (10) HP 3."
        ),
    }

    assert source_integrity_issues(bad) == ["embedded-stat-block:actions", "embedded-stat-block:rawText"]
    with pytest.raises(RuntimeError, match="parser contamination"):
        validate_monster_source_integrity([bad])


def test_bare_neighbor_name_bleed_fails_closed_without_a_second_stat_header() -> None:
    bad = {
        "name": "Snake",
        "traits": "",
        "actions": "Bite. Hit: 4 Piercing damage. Crab",
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": "Snake Tiny Beast. Actions Bite. Hit: 4 Piercing damage. Crab",
    }
    neighbor = {
        "name": "Crab",
        "traits": "Amphibious.",
        "actions": "Claw. Hit: 1 Bludgeoning damage.",
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": "Crab Tiny Beast. Amphibious. Actions Claw.",
    }

    assert source_integrity_issues(bad) == []
    assert neighbor_name_bleed_issues(bad, {"Snake", "Crab"}) == ["neighbor-name-bleed:Crab"]
    with pytest.raises(RuntimeError, match="neighbor-name-bleed:Crab"):
        validate_monster_source_integrity([bad, neighbor])


def test_interior_monster_reference_is_not_treated_as_neighbor_bleed() -> None:
    row = {
        "name": "Summoner",
        "traits": "",
        "actions": "Summon a Crab, then make one Staff attack.",
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": "Summoner. Actions. Summon a Crab, then make one Staff attack.",
    }

    assert neighbor_name_bleed_issues(row, {"Summoner", "Crab"}) == []
