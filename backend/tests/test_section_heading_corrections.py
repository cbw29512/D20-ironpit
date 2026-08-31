import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_neighbor_bleed_normalizer import normalize_neighbor_name_bleed
from app.content.monster_source_integrity import validate_monster_source_integrity


def _source_row(name: str, suffix: str) -> dict[str, object]:
    return {
        "name": name,
        "traits": "",
        "actions": f"Slam. Hit: 4 Bludgeoning damage. {suffix}",
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": f"{name}. Actions Slam. Hit: 4 Bludgeoning damage. {suffix}",
    }


def test_reviewed_section_headings_are_removed_from_catalog() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}

    assert not str(rows["Ogre Zombie"]["actions"]).endswith("Animals")
    assert not str(rows["Ogre Zombie"]["rawText"]).endswith("Animals")
    assert not str(rows["Phase Spider"]["bonusActions"]).endswith("Pirates")
    assert not str(rows["Phase Spider"]["rawText"]).endswith("Pirates")
    assert not str(rows["Ancient Brass Dragon"]["rawText"]).endswith("Bronze Dragons")


def test_unknown_section_heading_is_not_silently_normalized() -> None:
    row = _source_row("Test Beast", "Mystery Creatures")

    normalized = normalize_neighbor_name_bleed([row])

    assert str(normalized[0]["actions"]).endswith("Mystery Creatures")
    assert str(normalized[0]["rawText"]).endswith("Mystery Creatures")
    with pytest.raises(RuntimeError, match="terminal-heading-bleed:Mystery Creatures"):
        validate_monster_source_integrity(normalized)


def test_known_neighbor_monster_name_still_normalizes_generically() -> None:
    source = _source_row("Test Beast", "Crab")
    crab = _source_row("Crab", "Unrelated Heading")

    normalized = normalize_neighbor_name_bleed([source, crab])

    assert not str(normalized[0]["actions"]).endswith("Crab")
    assert not str(normalized[0]["rawText"]).endswith("Crab")
