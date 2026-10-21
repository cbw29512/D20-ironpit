from scripts.report_death_trigger_bindings_2014 import report


def test_death_trigger_source_inventory_covers_pinned_corpus():
    data = report()
    assert data["source_cards"] == 327
    assert data["cards_with_valid_death_trigger_identifiers"] <= data["cards_with_death_trigger_actions"]
    assert data["death_effect_dispatch_wired"] == 0
