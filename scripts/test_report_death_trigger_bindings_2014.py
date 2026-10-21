from scripts.report_death_trigger_bindings_2014 import report


def test_death_trigger_source_inventory_covers_pinned_corpus():
    data = report()
    assert data["source_cards_scanned"] == 327
    assert data["applicable_card_count"] == (
        data["wired_python_card_count"] + data["remaining_card_count"]
    )
    assert data["wired_python_card_count"] == data["wired_browser_card_count"]
    assert data["death_effect_dispatch_wired"] == data["wired_python_card_count"]
