from report_moving_darkness_actions_2014 import build_report


def test_full_moving_darkness_action_report() -> None:
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_card_count"] == 1
    assert report["wired_python_card_count"] == 1
    assert report["wired_browser_card_count"] == 1
    assert report["remaining_card_count"] == 0
    assert report["wired_cards"] == ["darkmantle"]
    assert report["exceptions"] == []
