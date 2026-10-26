from __future__ import annotations

from report_persistent_save_bindings_2014 import report


def test_persistent_save_report_scans_full_roster_and_wires_all_candidates() -> None:
    result = report()

    assert result["source_cards_scanned"] == 327
    assert result["applicable_card_count"] == 2
    assert result["applicable_cards"] == ["mummy", "mummy-lord"]
    assert result["wired_python_card_count"] == 2
    assert result["wired_browser_card_count"] == 2
    assert result["wired_cards"] == ["mummy", "mummy-lord"]
    assert result["delayed_source_component_card_count"] == 2
    assert result["delayed_source_component_cards"] == ["mummy", "mummy-lord"]
    assert result["arena_neutral_delayed_component_card_count"] == 2
    assert result["arena_neutral_delayed_component_cards"] == [
        "mummy",
        "mummy-lord",
    ]
    assert result["arena_active_delayed_component_card_count"] == 0
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
    assert result["status"] == "complete"
