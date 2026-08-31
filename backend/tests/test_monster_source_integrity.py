import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_integrity import source_integrity_issues, validate_monster_source_integrity


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
