from report_innate_sleep_bindings_2014 import report


def test_sleep_report_scans_every_card_and_verifies_python_browser_bindings() -> None:
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_cards"] == ["dust-mephit", "night-hag", "oni", "spirit-naga"]
    assert result["applicable_card_count"] == 4
    assert result["wired_python_card_count"] == 4
    assert result["wired_browser_card_count"] == 4
    assert result["remaining_card_count"] == 0
    assert len(result["exceptions"]) == 0
    assert result["wired_cards"] == ["dust-mephit", "night-hag", "oni", "spirit-naga"]
    assert result["shared_lifecycle_evidence"]["wake_action_id"] == "wake-sleeper"
