"""Pinned 2014 source proof and Python runtime regression for absent contexts."""
import logging

from app.content.monster_absent_context_source_2014 import (
    verified_absent_context_action_2014,
    verified_absent_context_trait_2014,
)
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.capability_compiler import compile_combatant
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_2014_source_exact_absent_context_promotes_two_without_erasing_attacks():
    try:
        sources = {item.id: item for item in load_monster_source_2014()}
        for monster_id, trait_names, action_name in (
            ("rust-monster", ("Iron Scent", "Rust Metal"), "Antennae"),
            ("nightmare", ("Confer Fire Resistance",), "Ethereal Stride"),
        ):
            source = sources[monster_id]
            snapshot = source.model_dump_json()
            assert all(verified_absent_context_trait_2014(source, name) for name in trait_names)
            assert verified_absent_context_action_2014(source, action_name)
            assert basic_blockers_2014(source) == ()
            template = compile_combatant(adapt_basic_monster_2014(source))
            assert template.ruleset == "2014"
            assert template.weapon_attack is not None
            assert source.model_dump_json() == snapshot
        assert "fire" in sources["nightmare"].damage_immunities
    except Exception:
        logger.exception("2014 absent-context source proof failed")
        raise


def test_2014_source_mutation_fails_closed():
    try:
        sources = {item.id: item for item in load_monster_source_2014()}
        rust = sources["rust-monster"]
        altered = rust.model_copy(update={
            "source_actions": (rust.source_actions or "").replace(
                "<strong>Antennae.</strong>",
                "<strong>Antennae.</strong> Also deals 2d8 fire damage.",
            )
        })
        assert not verified_absent_context_action_2014(altered, "Antennae")
        assert "source:extra-action" in basic_blockers_2014(altered)
        nightmare = sources["nightmare"]
        altered = nightmare.model_copy(update={
            "source_traits": (nightmare.source_traits or "").replace(
                "anyone riding it", "every creature in the arena"
            ),
        })
        assert not verified_absent_context_trait_2014(altered, "Confer Fire Resistance")
        assert "source:trait" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("2014 absent-context fail-closed source mutation failed")
        raise
