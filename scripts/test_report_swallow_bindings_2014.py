from pathlib import Path

from scripts.report_swallow_bindings_2014 import build_report, render

REPORT = Path("docs/generated/SWALLOW_BINDINGS_2014.json")


def test_swallow_inventory_covers_all_semantic_source_cards():
    data = build_report()
    assert data["source_cards_scanned"] == 327
    assert data["applicable_cards"] == [
        "behir", "giant-frog", "giant-toad", "kraken", "purple-worm",
        "remorhaz", "shambling-mound", "tarrasque",
    ]
    assert data["applicable_card_count"] == 8
    assert data["wired_python_card_count"] == 6
    assert data["wired_browser_card_count"] == 6
    assert data["wired_cards"] == [
        "behir", "giant-frog", "giant-toad", "kraken", "remorhaz", "tarrasque",
    ]
    assert data["remaining_card_count"] == 2
    assert {item["card_id"] for item in data["exceptions"]} == {
        "purple-worm", "shambling-mound",
    }
    assert data["status"] == "partial"


def test_swallow_generated_report_is_fresh():
    assert REPORT.read_text(encoding="utf-8") == render()
