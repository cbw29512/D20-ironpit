"""Roster-wide proof that the pinned Hydra is wired to universal heads."""
from scripts.report_variable_head_bindings_2014 import report


def test_variable_head_coverage_reports_compiled_hydra():
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_card_count"] == 1
    assert result["applicable_cards"] == ["hydra"]
    assert result["wired_python_card_count"] == 1
    assert result["wired_browser_card_count"] == 1
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
    assert result["status"] == "complete"
