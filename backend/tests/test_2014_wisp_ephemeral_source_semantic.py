"""2014 source-only equipment restriction cannot alter real combat."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_equipment_only_traits_2014 import source_proves_equipment_only_trait_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _wisp():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "will-o-wisp")
    except Exception:
        logger.exception("2014 source roster missing Will-o'-Wisp.")
        raise


def test_equipment_only_ability_is_unique_and_other_combat_blocks_remain():
    try:
        roster = load_monster_source_2014()
        matched = [
            m.id for m in roster
            if source_proves_equipment_only_trait_2014(m, "Ephemeral")
        ]
        assert len(roster) == 327
        assert matched == ["will-o-wisp"]
        source = _wisp()
        old = source.model_dump_json()
        assert verified_arena_inert_trait_2014(source, "Ephemeral")
        assert "Ephemeral" not in unsupported_traits_2014(source)
        assert "Consume Life" in unsupported_traits_2014(source)
        assert "source:trait" in basic_blockers_2014(source)
        assert "source:extra-action" in basic_blockers_2014(source)
        assert source.model_dump_json() == old
        # Card identity is not an ability dispatch rule.
        renamed = source.model_copy(update={
            "id": "unrelated-source", "name": "Unrelated Creature",
        })
        assert source_proves_equipment_only_trait_2014(renamed, "Ephemeral")
    except Exception:
        logger.exception("2014 equipment-only trait classification failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("can't wear or carry anything", "can wear armor"),
    ("can't wear or carry anything", "can't move while holding anything"),
    ("anything. </p>", "anything. Nearby creatures take 1d6 force damage.</p>"),
])
def test_changed_printed_trait_fails_closed(old: str, new: str):
    try:
        source = _wisp()
        assert old in source.source_traits
        changed = source.model_copy(update={
            "source_traits": source.source_traits.replace(old, new),
        })
        assert not source_proves_equipment_only_trait_2014(changed, "Ephemeral")
        assert "Ephemeral" in unsupported_traits_2014(changed)
    except Exception:
        logger.exception("Changed printed 2014 equipment trait was accepted.")
        raise


def test_unheaded_continuations_and_missing_trait_cannot_bypass_proof():
    try:
        source = _wisp()
        with_rider = source.model_copy(update={
            "source_traits": source.source_traits.replace(
                "anything. </p>",
                "anything.</p><p>The creature has resistance to fire damage.</p>",
            ),
        })
        assert not source_proves_equipment_only_trait_2014(with_rider, "Ephemeral")
        assert "Ephemeral" in unsupported_traits_2014(with_rider)
        missing = source.model_copy(update={
            "trait_names": [x for x in source.trait_names if x != "Ephemeral"],
        })
        assert not source_proves_equipment_only_trait_2014(missing, "Ephemeral")
        assert not source_proves_equipment_only_trait_2014(source, "Consume Life")
    except Exception:
        logger.exception("2014 equipment-only source extension was accepted.")
        raise
