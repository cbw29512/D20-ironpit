from report_smother_bindings_2014 import build_report


def test_smother_report_scans_full_2014_catalog_and_is_complete():
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_card_count"] == 1
    assert report["wired_python_card_count"] == 1
    assert report["wired_browser_card_count"] == 1
    assert report["remaining_card_count"] == 0
    assert report["wired_cards"] == ["rug-of-smothering"]
    assert report["exceptions"] == []
