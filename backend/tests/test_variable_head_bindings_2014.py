"""Roster-wide fail-closed proof for the generic variable-head binding."""
from scripts.report_variable_head_bindings_2014 import report


def test_variable_head_coverage_reports_missing_source_parameters():
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_card_count"] == 1
    assert result["wired_python_card_count"] == 0
    assert result["wired_browser_card_count"] == 0
    assert result["remaining_card_count"] == 1
    assert len(result["exceptions"]) == 1
    assert "incomplete semantic clauses" in result["exceptions"][0]["reason"]
