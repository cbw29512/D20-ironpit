"""2014 Drow-family Faerie Fire: exact source, shared spell, uses and browser data."""
from __future__ import annotations

import logging

import pytest

from app.content.druid_2014_level1_spells import faerie_fire_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_innate_faerie_fire_2014 import (
    source_proven_innate_faerie_fire_2014,
)
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import (
    innate_alternate_spell_casts_2014,
    innate_spell_resources_2014,
    supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import _spell

logger = logging.getLogger(__name__)

_EXPECTED = {"drow": 11, "drider": 13}


def _card(monster_id: str):
    try:
        rows = load_monster_source_2014()
        assert len(rows) == 327
        return next(row for row in rows if row.id == monster_id)
    except Exception:
        logger.exception("Unable to load 2014 source for %s.", monster_id)
        raise


@pytest.mark.parametrize("monster_id,dc", _EXPECTED.items())
def test_innate_faerie_fire_reuses_2014_druid_spell(monster_id: str, dc: int):
    try:
        card = _card(monster_id)
        original = card.model_dump_json()
        source = source_proven_innate_faerie_fire_2014(card)
        assert source == [faerie_fire_2014(dc)]
        assert [item.id for item in innate_spell_save_actions_2014(card)] == ["faerie-fire"]
        spell = source[0]
        assert (spell.name, spell.level, spell.range_ft, spell.dc) == (
            "Faerie Fire", 1, 60, dc,
        )
        assert spell.area.shape == "cube" and spell.area.length_ft == 20
        assert spell.save_ability == "dexterity" and spell.concentration
        assert spell.duration_minutes == 1
        assert [x.kind for x in spell.failed_save_modifier_effects] == [
            "attacks-against-advantage", "invisibility-benefits-suppressed",
        ]
        serialized = _spell(spell)
        assert serialized["area"]["shape"] == "cube"
        assert serialized["dc"] == dc
        assert serialized["failedSaveModifierEffects"][1]["kind"] == (
            "invisibility-benefits-suppressed"
        )
        assert sorted((r.id, r.max_uses) for r in innate_spell_resources_2014(card)) == [
            ("darkness", 1), ("faerie-fire", 1),
        ]
        grants = [g for g in innate_alternate_spell_casts_2014(card)
                  if g.spell_id == "faerie-fire"]
        assert len(grants) == 1
        assert (grants[0].cast_level, grants[0].resource_id,
                grants[0].resource_cost) == (1, "faerie-fire", 1)
        # Darkness is independently attached through the generic obscuration
        # zone. No source spellcasting blocker remains for either card.
        assert supports_innate_spellcasting_2014(card)
        assert "mechanic:spellcasting" not in basic_blockers_2014(card)
        assert card.model_dump_json() == original
        renamed = card.model_copy(update={
            "id": "anonymous-fiend", "name": "Synthetic Monster",
        })
        assert source_proven_innate_faerie_fire_2014(renamed) == source
    except Exception:
        logger.exception("Innate Faerie Fire source binding failed for %s.", monster_id)
        raise


@pytest.mark.parametrize("before,after", [
    ("dancing lights", "magic missile"),
    ("1/day each: darkness, faerie fire", "1/day each: faerie fire"),
    ("faerie fire", "fireball"),
    ("requiring no material components", "requiring material components"),
])
@pytest.mark.parametrize("monster_id", list(_EXPECTED))
def test_source_fingerprint_mutation_fails_closed(monster_id, before, after):
    try:
        card = _card(monster_id)
        assert before in card.source_traits
        altered = card.model_copy(update={
            "source_traits": card.source_traits.replace(before, after),
        })
        assert not source_proven_innate_faerie_fire_2014(altered)
    except Exception:
        logger.exception("2014 source mutation test failed for %s/%s.", monster_id, before)
        raise


@pytest.mark.parametrize("monster_id", list(_EXPECTED))
def test_structured_innate_resource_mutation_fails_closed(monster_id):
    try:
        card = _card(monster_id)
        altered = card.innate_spellcasting.copy()
        altered["spells"] = [dict(row) for row in altered["spells"]]
        for spell in altered["spells"]:
            if spell["id"] == "faerie-fire":
                spell["uses_per_day"] = 2
        damaged = card.model_copy(update={"innate_spellcasting": altered})
        assert not source_proven_innate_faerie_fire_2014(damaged)
        assert "faerie-fire" not in [
            x.id for x in innate_spell_save_actions_2014(damaged)
        ]
    except Exception:
        logger.exception("2014 innate usage audit failed for %s.", monster_id)
        raise
