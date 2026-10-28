from report_innate_ray_of_enfeeblement_bindings_2014 import report


def test_report_scans_and_wires_every_ray_of_enfeeblement_card() -> None:
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_cards"] == ["night-hag"]
    assert result["applicable_card_count"] == 1
    assert result["wired_python_card_count"] == 1
    assert result["wired_browser_card_count"] == 1
    assert result["wired_cards"] == ["night-hag"]
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
    assert result["source_cards_2024_audited"] == 330
    assert result["applicable_2024_card_count"] == 0
    assert result["applicable_2024_cards"] == []
    assert result["status"] == "complete"
