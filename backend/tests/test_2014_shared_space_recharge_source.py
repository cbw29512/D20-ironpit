"""Audit source-only shared-square Recharge headers across all 327 cards."""
from __future__ import annotations

from app.content.monster_shared_space_recharge_2014 import (
    source_shared_space_recharge_headers_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014


def _sources():
    rows = load_monster_source_2014()
    assert len(rows) == 327
    return {row.id: row for row in rows}


def test_exact_cross_roster_headers_and_unimplemented_riders() -> None:
    rows = _sources()
    found = {
        (card.id, item.action_id): item
        for card in rows.values()
        for item in source_shared_space_recharge_headers_2014(card)
    }
    assert set(found) == {
        ("air-elemental", "whirlwind"),
        ("water-elemental", "whelm"),
    }
    whirlwind = found["air-elemental", "whirlwind"]
    whelm = found["water-elemental", "whelm"]
    assert (whirlwind.source_name, whirlwind.recharge_minimum) == ("Whirlwind", 4)
    assert (whirlwind.save_dc, whirlwind.save_ability) == (13, "strength")
    assert (whelm.source_name, whelm.recharge_minimum) == ("Whelm", 4)
    assert (whelm.save_dc, whelm.save_ability) == (15, "strength")
    # Header proof is intentionally not an implementation or clearance.
    assert "On a failure" in whirlwind.unbound_outcomes
    assert "On a failure" in whelm.unbound_outcomes


def test_malformed_header_or_source_resource_cannot_pass() -> None:
    card = _sources()["water-elemental"]
    broken = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "Each creature in the elemental's space",
            "Each creature near the elemental",
        ),
    })
    assert source_shared_space_recharge_headers_2014(broken) == ()
    wrong_recharge = card.model_copy(update={
        "action_recharges": {"whelm": 5},
    })
    assert source_shared_space_recharge_headers_2014(wrong_recharge) == ()


def test_renamed_action_still_compiles_source_header() -> None:
    card = _sources()["water-elemental"]
    renamed = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "Whelm (Recharge 4–6)", "Flood (Recharge 4–6)",
        ),
        "action_names": [
            name.replace("Whelm (Recharge 4–6)", "Flood (Recharge 4–6)")
            for name in card.action_names
        ],
        "action_recharges": {"flood": 4},
    })
    result = source_shared_space_recharge_headers_2014(renamed)
    assert len(result) == 1
    assert (result[0].action_id, result[0].source_name) == ("flood", "Flood")
