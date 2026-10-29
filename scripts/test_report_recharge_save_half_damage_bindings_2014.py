from report_recharge_save_half_damage_bindings_2014 import build_report


def test_all_2014_recharge_save_half_damage_cards_are_wired() -> None:
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_card_count"] == 30
    assert report["wired_python_card_count"] == 30
    assert report["wired_browser_card_count"] == 30
    assert report["remaining_card_count"] == 0
    assert report["exceptions"] == []
    assert "behir" in report["wired_cards"]
