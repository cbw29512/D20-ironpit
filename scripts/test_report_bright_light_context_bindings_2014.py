from report_bright_light_context_bindings_2014 import build_report


def test_full_bright_light_context_report() -> None:
    report = build_report()
    assert report["source_cards_scanned"] == 327
    assert report["applicable_card_count"] == 8
    assert report["wired_python_card_count"] == 5
    assert report["wired_browser_card_count"] == 5
    assert report["remaining_card_count"] == 3
    assert set(report["wired_cards"]) == {
        "azer", "cloaker", "fire-elemental", "giant-fire-beetle", "nightmare",
    }
    assert {item["card_id"] for item in report["exceptions"]} == {
        "flameskull", "magmin", "will-o-wisp",
    }
