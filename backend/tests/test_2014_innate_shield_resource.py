"""Innate Shield keeps its printed daily-use resource, never a fake slot."""
from __future__ import annotations

import logging

from app.combat.reaction_defense_spells import reaction_defense_blocks_auto_hit
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monster_shield_reaction_2014 import (
    source_shield_reaction_2014, source_shield_reaction_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def test_couatl_shield_uses_printed_innate_pool_and_no_spell_slots():
    try:
        card = next(row for row in load_monster_source_2014() if row.name == "Couatl")
        defense = source_shield_reaction_2014(card)
        assert defense is not None
        assert defense.minimum_slot_level is None
        assert defense.resource_id == "shield"
        resources = source_shield_reaction_resources_2014(card)
        source = next(row for row in card.innate_spellcasting["spells"] if row["id"] == "shield")
        assert len(resources) == 1
        assert resources[0].max_uses == source["uses_per_day"]
        state = build_combatant_state(build_demo_fighter().model_copy(update={
            "reaction_defense_spell": defense,
            "resources": resources,
        }))
        assert reaction_defense_blocks_auto_hit(state, "magic-missile", source_id="couatl-1")
        assert state.resources[0].current_uses == resources[0].max_uses - 1
        assert not state.reaction_available
    except Exception:
        logger.exception("Couatl innate Shield resource semantics failed")
        raise


def test_prepared_mage_has_no_innate_shield_daily_pool():
    try:
        card = next(row for row in load_monster_source_2014() if row.name == "Mage")
        defense = source_shield_reaction_2014(card)
        assert defense is not None
        assert defense.minimum_slot_level == 1 and defense.resource_id is None
        assert source_shield_reaction_resources_2014(card) == []
    except Exception:
        logger.exception("Prepared Mage was incorrectly granted innate Shield")
        raise
