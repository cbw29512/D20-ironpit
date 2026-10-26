from pathlib import Path

from scripts.report_death_trigger_bindings_2014 import render, report

REPORT = Path("docs/generated/DEATH_TRIGGER_BINDINGS_2014.json")


def test_death_trigger_source_inventory_covers_pinned_corpus():
    data = report()
    assert data["source_cards_scanned"] == 327
    assert data["applicable_cards"] == [
        "balor", "dust-mephit", "ice-mephit", "magma-mephit", "magmin",
        "steam-mephit",
    ]
    assert data["applicable_card_count"] == 6
    assert data["structured_source_card_count"] == 4
    assert data["source_declared_card_count"] == 6
    assert data["wired_python_card_count"] == 6
    assert data["wired_browser_card_count"] == 6
    assert data["wired_cards"] == data["applicable_cards"]
    assert data["remaining_card_count"] == 0
    assert data["exceptions"] == []
    assert data["death_effect_dispatch_wired"] == 6
    assert data["status"] == "complete"


def test_death_trigger_generated_report_is_fresh():
    assert REPORT.read_text(encoding="utf-8") == render()
