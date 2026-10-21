"""Roster-wide 2014 armor-class wiring contract.

All 327 source cards own their printed AC. Only source-admitted cards are
executable; blocked cards are never silently represented as runnable.
"""
from __future__ import annotations

import logging

from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014
from app.combat.modifier_stack import effective_armor_class
from app.combat.state import build_combatant_state
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)

EXPECTED_SOURCE_COUNT = 327
EXPECTED_ADMITTED_COUNT = 237


def test_all_2014_source_cards_have_valid_unique_ac() -> None:
    """Validate every source card, not merely already-admitted monsters."""
    try:
        sources = load_monster_source_2014()
        assert len(sources) == EXPECTED_SOURCE_COUNT
        assert len({source.id for source in sources}) == EXPECTED_SOURCE_COUNT
        for source in sources:
            assert source.ruleset == "2014", source.id
            assert type(source.armor_class) is int and source.armor_class >= 1, source.id
    except Exception:
        logger.exception("2014 full-roster source AC validation failed")
        raise


def test_every_admitted_2014_ac_reaches_python_and_browser_template() -> None:
    """Source AC must survive both compilation and browser serialization unchanged."""
    try:
        sources = {source.id: source for source in load_monster_source_2014()}
        templates = build_basic_2014_monsters()
        assert len(templates) == EXPECTED_ADMITTED_COUNT
        assert len({template.id for template in templates}) == EXPECTED_ADMITTED_COUNT
        for template in templates:
            # The canonical adapter prefixes source IDs with the 2014 edition.
            assert template.id.startswith("2014-"), template.id
            source_id = template.id.removeprefix("2014-")
            assert source_id in sources, template.id
            original = sources[source_id]
            assert template.armor_class == original.armor_class, template.id
            assert template.kind == "monster" and template.ruleset == "2014"
            row = template_row(template)
            assert row["armor_class"] == original.armor_class, template.id
            # Effective AC is derived from the immutable card and fresh fight state.
            state = build_combatant_state(template)
            assert effective_armor_class(state) == original.armor_class, template.id
            assert state.template.armor_class == original.armor_class, template.id
    except Exception:
        logger.exception("2014 admitted monster AC compiler/browser parity failed")
        raise
