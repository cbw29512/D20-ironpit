from report_damage_transfer_bindings_2014 import build_report


def test_all_2014_damage_transfer_cards_are_wired() -> None:
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_card_count"] == 2
    assert report["wired_python_card_count"] == 2
    assert report["wired_browser_card_count"] == 2
    assert report["remaining_card_count"] == 0
    assert report["exceptions"] == []
    assert report["wired_cards"] == ["cloaker", "rug-of-smothering"]
