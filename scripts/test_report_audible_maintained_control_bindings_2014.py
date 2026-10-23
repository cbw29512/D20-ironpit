from scripts.report_audible_maintained_control_bindings_2014 import report


def test_audible_maintained_control_inventory_covers_pinned_corpus():
    data = report()
    assert data["source_cards_scanned"] == 327
    assert data["applicable_card_count"] == (
        data["wired_python_card_count"] + data["remaining_card_count"]
    )
    assert data["wired_python_card_count"] == data["wired_browser_card_count"]
    assert data["applicable_cards"] == ["harpy"]
    assert data["wired_python_card_count"] == 1
    assert data["remaining_card_count"] == 0
    assert data["exceptions"] == []
    assert data["status"] == "complete"
