"""2014-only spell data is separate from immutable monster source access."""
from __future__ import annotations

import json

import pytest

from app.content.monster_sleep_spell_source_2014 import sleep_spell_rules_2014
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_pinned_2014_sleep_source_is_complete_and_not_2024():
    source = sleep_spell_rules_2014()
    assert source.ruleset == "2014"
    assert source.spell_id == "sleep"
    assert (source.pool_dice_count, source.pool_dice_size,
            source.pool_extra_dice_per_upcast_level) == (5, 8, 2)
    assert (source.range_ft, source.area_radius_ft, source.duration_rounds) == (90, 20, 10)
    assert source.target_order == "ascending_current_hp"
    assert source.excluded_creature_types == ["undead"]
    assert source.excluded_condition_immunities == ["charmed"]
    assert source.allowed_removal_action_ids == ["wake-sleeper"]
    assert source.ends_on_damage
    assert source.concentration is False


@pytest.mark.parametrize("field,value", [
    ("ruleset", "2024"), ("range_ft", 60),
    ("pool_dice_count", 0), ("pool_extra_dice_per_upcast_level", 3),
    ("excluded_condition_immunities", []),
    ("allowed_removal_action_ids", []), ("unexpected_combat_field", True),
])
def test_unknown_or_mutated_source_fails_closed(field, value, tmp_path, monkeypatch):
    from app.content import monster_sleep_spell_source_2014 as module
    original = sleep_spell_rules_2014().model_dump()
    original[field] = value
    target = tmp_path / "sleep.json"
    target.write_text(json.dumps(original), encoding="utf-8")
    monkeypatch.setattr(module, "_PATH", target)
    with pytest.raises(Exception):
        module.sleep_spell_rules_2014()


def test_whole_roster_sleep_access_is_independent_of_shared_source():
    monsters = load_monster_source_2014()
    assert len(monsters) == 327
    source = sleep_spell_rules_2014()
    ids = set()
    for monster in monsters:
        innate = any(str(row.get("id") or "") == source.spell_id
                     for row in innate_spells_2014(monster))
        prepared = monster.spellcasting
        prepared_row = prepared if isinstance(prepared, dict) else (
            prepared.model_dump() if prepared else {}
        )
        declared = any(str(row.get("id") or "") == source.spell_id
                       for row in (prepared_row.get("spells") or []))
        if innate or declared:
            ids.add(monster.id)
    assert ids == {"dust-mephit", "night-hag", "oni", "spirit-naga"}
