from report_end_turn_recurring_damage_bindings_2014 import report


def test_end_turn_recurring_damage_report_uses_locked_no_douse_ai() -> None:
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_cards"] == ["magmin"]
    assert result["applicable_card_count"] == 1
    assert result["wired_python_card_count"] == 1
    assert result["wired_browser_card_count"] == 1
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
    assert result["wired_cards"] == ["magmin"]
    assert result["status"] == "complete"
    assert result["source_declared_parameters"][0]["tick_timing"] == "target_turn_end"
