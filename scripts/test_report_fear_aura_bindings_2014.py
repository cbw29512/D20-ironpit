from __future__ import annotations

from report_fear_aura_bindings_2014 import report


def test_fear_aura_report_scans_and_wires_all_candidates() -> None:
    result = report()

    assert result["source_cards_scanned"] == 327
    assert result["applicable_card_count"] == 1
    assert result["applicable_cards"] == ["pit-fiend"]
    assert result["wired_python_card_count"] == 1
    assert result["wired_browser_card_count"] == 1
    assert result["wired_cards"] == ["pit-fiend"]
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
    assert result["status"] == "complete"
