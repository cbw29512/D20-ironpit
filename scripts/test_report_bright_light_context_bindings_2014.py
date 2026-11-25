from report_bright_light_context_bindings_2014 import build_report


def test_full_bright_light_context_report() -> None:
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_card_count"] == 8
    assert report["wired_python_card_count"] == 8
    assert report["wired_browser_card_count"] == 8
    assert report["remaining_card_count"] == 0
    assert set(report["wired_cards"]) == {
        "azer", "cloaker", "fire-elemental", "flameskull",
        "giant-fire-beetle", "magmin", "nightmare", "will-o-wisp",
    }
    assert report["exceptions"] == []
