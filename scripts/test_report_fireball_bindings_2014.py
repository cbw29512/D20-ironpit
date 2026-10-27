from __future__ import annotations

from report_fireball_bindings_2014 import report


def test_fireball_report_scans_and_wires_all_candidates() -> None:
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_cards"] == ["pit-fiend"]
    assert result["applicable_card_count"] == 1
    assert result["wired_python_card_count"] == 1
    assert result["wired_browser_card_count"] == 1
    assert result["wired_cards"] == ["pit-fiend"]
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
    assert result["status"] == "complete"
