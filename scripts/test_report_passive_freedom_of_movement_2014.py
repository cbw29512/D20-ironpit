from report_passive_freedom_of_movement_2014 import build_report


def test_passive_freedom_of_movement_report_covers_full_roster() -> None:
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_card_count"] == 1
    assert report["wired_python_card_count"] == 1
    assert report["wired_browser_card_count"] == 1
    assert report["remaining_card_count"] == 0
    assert report["wired_cards"] == ["kraken"]
    assert report["exceptions"] == []
    assert report["paired_2024_reuse"]["source_cards_scanned"] == 330
    assert report["paired_2024_reuse"]["applicable_card_count"] == 0
    assert report["paired_2024_reuse"]["applicable_cards"] == []
