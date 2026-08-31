import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_integrity import (
    neighbor_name_bleed_issues,
    source_integrity_issues,
    terminal_heading_bleed_issues,
    validate_monster_source_integrity,
)


def _row(name: str, actions: str, raw_text: str) -> dict[str, object]:
    return {
        "name": name,
        "traits": "",
        "actions": actions,
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": raw_text,
    }


def test_corrected_srd_catalog_has_no_embedded_stat_blocks() -> None:
    rows = load_monster_rows()
    assert all(source_integrity_issues(row) == [] for row in rows)


def test_embedded_neighbor_stat_block_fails_closed() -> None:
    bad = _row(
        "Snake",
        "Bite. Hit: 4. Crab Tiny Beast AC 11 Initiative +0 (10) HP 3 (1d4 + 1)",
        "AC 13 Initiative +2 (12) HP 13. Actions Bite. Crab Tiny Beast AC 11 Initiative +0 (10) HP 3.",
    )

    assert source_integrity_issues(bad) == ["embedded-stat-block:actions", "embedded-stat-block:rawText"]
    with pytest.raises(RuntimeError, match="parser contamination"):
        validate_monster_source_integrity([bad])


def test_bare_neighbor_name_bleed_fails_closed_without_a_second_stat_header() -> None:
    bad = _row(
        "Snake",
        "Bite. Hit: 4 Piercing damage. Crab",
        "Snake Tiny Beast. Actions Bite. Hit: 4 Piercing damage. Crab",
    )
    neighbor = _row("Crab", "Claw. Hit: 1 Bludgeoning damage.", "Crab Tiny Beast. Actions Claw.")

    assert source_integrity_issues(bad) == []
    assert neighbor_name_bleed_issues(bad, {"Snake", "Crab"}) == ["neighbor-name-bleed:Crab"]
    with pytest.raises(RuntimeError, match="neighbor-name-bleed:Crab"):
        validate_monster_source_integrity([bad, neighbor])


def test_longest_terminal_monster_name_wins_suffix_ambiguity() -> None:
    row = _row(
        "Pegasus",
        "Hooves. Hit: 12 Radiant damage. Phase Spider",
        "Pegasus. Actions Hooves. Hit: 12 Radiant damage. Phase Spider",
    )

    assert neighbor_name_bleed_issues(row, {"Pegasus", "Phase Spider", "Spider"}) == [
        "neighbor-name-bleed:Phase Spider"
    ]


def test_non_monster_terminal_section_heading_fails_closed() -> None:
    row = _row(
        "Ogre Zombie",
        "Slam. Hit: 13 Bludgeoning damage. Animals",
        "Ogre Zombie. Actions Slam. Hit: 13 Bludgeoning damage. Animals",
    )

    assert terminal_heading_bleed_issues(row, {"Ogre Zombie"}) == ["terminal-heading-bleed:Animals"]
    with pytest.raises(RuntimeError, match="terminal-heading-bleed:Animals"):
        validate_monster_source_integrity([row])


def test_interior_monster_reference_is_not_treated_as_neighbor_bleed() -> None:
    row = _row(
        "Summoner",
        "Summon a Crab, then make one Staff attack.",
        "Summoner. Actions. Summon a Crab, then make one Staff attack.",
    )

    assert neighbor_name_bleed_issues(row, {"Summoner", "Crab"}) == []
    assert terminal_heading_bleed_issues(row, {"Summoner", "Crab"}) == []
