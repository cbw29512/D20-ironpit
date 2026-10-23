from __future__ import annotations

from pathlib import Path

from app.content.monster_forced_displacement_2014 import forced_displacement_inventory_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.report_forced_displacement_2014 import render

ROOT = Path(__file__).resolve().parents[2]


def test_forced_displacement_inventory_scans_all_2014_cards() -> None:
    report = forced_displacement_inventory_2014(load_monster_source_2014())

    assert report["source_card_count"] == 327
    assert report["applicable_card_count"] == 17
    assert report["python_wired_card_count"] == 6
    assert report["browser_wired_card_count"] == 6
    assert report["remaining_card_count"] == 11
    assert {row["monster_id"] for row in report["exceptions"]} == {
        "air-elemental",
        "balor",
        "bulette",
        "djinni",
        "gelatinous-cube",
        "ice-devil",
        "kraken",
        "minotaur",
        "minotaur-skeleton",
        "roper",
        "water-elemental",
    }


def test_forced_displacement_generated_report_is_current() -> None:
    output = ROOT / "docs" / "generated" / "FORCED_DISPLACEMENT_2014.json"
    assert output.read_text(encoding="utf-8") == render()
