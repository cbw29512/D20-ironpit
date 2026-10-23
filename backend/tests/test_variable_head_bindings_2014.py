"""Roster-wide source proof for the generic variable-head binding."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_variable_heads_2014 import variable_head_profile_2014
from scripts.report_variable_head_bindings_2014 import report


def test_semantic_scan_binds_source_parameters_without_identity_dispatch():
    cards = load_monster_source_2014()
    profiles = [(card, variable_head_profile_2014(card)) for card in cards]
    profiles = [(card, profile) for card, profile in profiles if profile is not None]
    assert len(cards) == 327
    assert len(profiles) == 1
    card, profile = profiles[0]
    assert profile.initial_heads == 5
    assert profile.sever_damage_threshold == 25
    assert profile.heads_per_regrowth == 2
    assert profile.healing_per_regrown_head == 10
    assert profile.regrowth_blocking_damage_types == ["fire"]
    assert profile.source_name in card.trait_names
    assert profile.reaction_source_name in card.trait_names


def test_variable_head_coverage_report_is_complete():
    result = report()
    assert result["source_cards_scanned"] == 327
    assert result["applicable_card_count"] == 1
    assert result["wired_python_card_count"] == 1
    assert result["wired_browser_card_count"] == 1
    assert result["remaining_card_count"] == 0
    assert result["exceptions"] == []
