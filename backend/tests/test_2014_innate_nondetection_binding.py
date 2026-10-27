from __future__ import annotations

from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_innate_source_2014 import (
    ARENA_NEUTRAL_INNATE_SPELLS_2014,
    innate_spells_2014,
)
from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _source(monster_id: str):
    return next(card for card in load_monster_source_2014() if card.id == monster_id)


def test_every_innate_nondetection_row_is_preserved_and_arena_neutral() -> None:
    applicable = [
        card for card in load_monster_source_2014()
        if any(row.get("id") == "nondetection" for row in innate_spells_2014(card))
    ]
    assert [card.id for card in applicable] == ["deep-gnome-svirfneblin"]
    row, = [row for row in innate_spells_2014(applicable[0]) if row.get("id") == "nondetection"]
    assert row == {
        "id": "nondetection",
        "name": "nondetection",
        "usage": "at_will",
        "uses_per_day": None,
        "shared_pool": False,
        "qualifier": "self only",
    }
    assert "nondetection" in ARENA_NEUTRAL_INNATE_SPELLS_2014
    assert supports_innate_spellcasting_2014(applicable[0]) is True


def test_nondetection_classification_is_semantic_and_creates_no_combat_effect() -> None:
    source = _source("deep-gnome-svirfneblin")
    renamed = source.model_copy(update={"name": "Synthetic"})
    assert supports_innate_spellcasting_2014(renamed) is True
    definition = adapt_basic_monster_2014(renamed)
    assert all(action.id != "nondetection" for action in definition.timed_self_buff_actions)
    assert all(action.id != "nondetection" for action in definition.spell_save_actions)
    assert all(resource.id != "nondetection" for resource in definition.resources)
