"""Drow-family Darkness: pinned source, universal schema and resource contract."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_darkness_2014 import source_proven_innate_darkness_2014
from app.content.monster_innate_support_2014 import (
    innate_spell_resources_2014, supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _suppression_zone

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("monster_id,dc", [("drow", 11), ("drider", 13)])
def test_printed_darkness_attaches_generic_zone_and_one_daily_resource(monster_id, dc):
    try:
        card = next(x for x in load_monster_source_2014() if x.id == monster_id)
        snapshot = card.model_dump_json()
        (action,) = source_proven_innate_darkness_2014(card)
        assert (action.name, action.id, action.level, action.radius_ft,
                action.cast_range_ft) == ("Darkness", "darkness", 2, 15, 60)
        assert (action.duration_rounds, action.concentration,
                action.obscuration_kind) == (100, True, "magical-darkness")
        assert not any((action.deafens, action.blocks_verbal_spells,
                        action.thunder_immunity, action.expends_spell_slot))
        assert (action.resource_id, action.resource_cost) == ("darkness", 1)
        serialized = _suppression_zone(action)
        assert serialized["obscurationKind"] == "magical-darkness"
        assert serialized["radiusFt"] == 15
        assert serialized["resourceId"] == "darkness"
        assert supports_innate_spellcasting_2014(card)
        assert "mechanic:spellcasting" not in basic_blockers_2014(card)
        assert {(r.id, r.max_uses) for r in innate_spell_resources_2014(card)} == {
            ("faerie-fire", 1), ("darkness", 1),
        }
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        assert template.suppression_zone_actions[0].name == "Darkness"
        assert template.spell_save_actions[0].dc == dc
        assert card.model_dump_json() == snapshot
        renamed = card.model_copy(update={"id": "anonymous-monster", "name": "Other"})
        assert source_proven_innate_darkness_2014(renamed) == [action]
    except Exception:
        logger.exception("2014 innate Darkness binding failed for %s.", monster_id)
        raise


@pytest.mark.parametrize("monster_id", ["drow", "drider"])
@pytest.mark.parametrize("old,new", [
    ("dancing lights", "fireball"),
    ("1/day each: darkness, faerie fire", "2/day each: darkness, faerie fire"),
    ("requiring no material components", "requiring rare components"),
])
def test_innate_darkness_source_changes_fail_closed(monster_id, old, new):
    try:
        card = next(x for x in load_monster_source_2014() if x.id == monster_id)
        assert old in card.source_traits
        altered = card.model_copy(update={"source_traits": card.source_traits.replace(old, new)})
        assert source_proven_innate_darkness_2014(altered) == []
    except Exception:
        logger.exception("2014 Darkness source mutation failed: %s", old)
        raise
