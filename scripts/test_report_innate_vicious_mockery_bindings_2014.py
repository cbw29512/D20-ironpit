from __future__ import annotations

from report_innate_vicious_mockery_bindings_2014 import report


def test_innate_vicious_mockery_report_scans_and_wires_all_candidates() -> None:
    result = report()
    expected = ["green-hag"]
    assert result["source_cards_scanned"] == 327
    assert result["applicable_cards"] == expected
    assert result["applicable_card_count"] == 1
    assert result["wired_python_card_count"] == 1
    assert result["wired_browser_card_count"] == 1
    assert result["wired_cards"] == expected
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
    assert result["status"] == "complete"
