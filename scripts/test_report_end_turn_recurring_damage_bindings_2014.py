from report_end_turn_recurring_damage_bindings_2014 import report


def test_end_turn_recurring_damage_report_fails_closed_on_missing_action_range() -> None:
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_cards"] == ["magmin"]
    assert result["applicable_card_count"] == 1
    assert result["wired_python_card_count"] == 0
    assert result["wired_browser_card_count"] == 0
    assert result["remaining_card_count"] == 1
    assert result["exceptions"] == [{
        "monster": "magmin",
        "reason": (
            "source permits a creature to douse the fire but omits the grid range "
            "for a different creature performing that Action"
        ),
        "missing_fields": ["removal_action_range_ft"],
    }]
    assert result["source_declared_parameters"][0]["tick_timing"] == "target_turn_end"
