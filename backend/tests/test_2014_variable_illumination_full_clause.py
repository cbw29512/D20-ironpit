"""Cross-roster strict source proof for 2014 Variable Illumination."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_ignited_illumination_2014 import source_proves_light_only_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _wisp():
    return next(m for m in load_monster_source_2014() if m.id == "will-o-wisp")


def test_complete_327_card_light_only_source_family():
    try:
        roster = load_monster_source_2014()
        matches = [
            (m.id, name) for m in roster
            for name in ("Ignited Illumination", "Variable Illumination")
            if source_proves_light_only_2014(m, name)
        ]
        assert len(roster) == 327
        assert matches == [
            ("magmin", "Ignited Illumination"),
            ("will-o-wisp", "Variable Illumination"),
        ]
        card = _wisp()
        before = card.model_dump_json()
        assert verified_arena_inert_trait_2014(card, "Variable Illumination")
        assert "Variable Illumination" not in unsupported_traits_2014(card)
        assert card.model_dump_json() == before
        renamed = card.model_copy(update={"id": "other-light-source", "name": "Other Source"})
        assert source_proves_light_only_2014(renamed, "Variable Illumination")
    except Exception:
        logger.exception("Full 2014 lighting source-family proof failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("5- to 20-foot radius", "5- to 40-foot radius"),
    ("dim light for an additional number of feet", "1d6 fire damage to nearby creatures"),
    ("alter the radius as a bonus action", "alter the radius as a reaction"),
    ("a bonus action.</p>", "a bonus action. A target then makes a saving throw.</p>"),
])
def test_variable_illumination_mutations_fail_closed(old: str, new: str):
    card = _wisp()
    assert old in (card.source_traits or "")
    mutated = card.model_copy(update={
        "source_traits": (card.source_traits or "").replace(old, new),
    })
    assert not source_proves_light_only_2014(mutated, "Variable Illumination")
    assert "Variable Illumination" in unsupported_traits_2014(mutated)


def test_variable_illumination_requires_printed_heading_and_no_hidden_rider():
    card = _wisp()
    without_trait = card.model_copy(update={
        "trait_names": [t for t in card.trait_names if t != "Variable Illumination"],
    })
    assert not source_proves_light_only_2014(without_trait, "Variable Illumination")
    with_rider = card.model_copy(update={
        "source_traits": (card.source_traits or "")
        + "<p>Adjacent creatures take force damage each turn.</p>",
    })
    assert not source_proves_light_only_2014(with_rider, "Variable Illumination")
    assert "Variable Illumination" in unsupported_traits_2014(with_rider)


def test_light_only_proof_rejects_unrelated_combat_traits():
    """A lighting source cannot classify a combat ability as arena-neutral."""
    try:
        assert not source_proves_light_only_2014(_wisp(), "Consume Life")
        assert not source_proves_light_only_2014(_wisp(), "Ephemeral")
        assert not source_proves_light_only_2014(_wisp(), "not-a-printed-trait")
    except Exception:
        logger.exception("Unrelated combat trait was considered lighting-only.")
        raise
