from types import SimpleNamespace

import pytest

from app.content.monster_prepared_spells_2014 import prepared_spell_actions_2014


def _monster(spells, *, complete=True):
    return SimpleNamespace(
        name="Source-defined Cleric", abilities={"strength": 10, "dexterity": 10, "constitution": 10,
                                              "intelligence": 10, "wisdom": 14, "charisma": 10},
        spellcasting={"source_complete": complete, "save_dc": 12,
                      "spells": [{"id": spell, "level": 0 if spell in {"sacred-flame", "light", "thaumaturgy"} else 1}
                                 for spell in spells]},
    )


def test_shared_pregen_spell_builders_are_used_for_monsters():
    result = prepared_spell_actions_2014(_monster(
        ["sacred-flame", "bless", "cure-wounds", "sanctuary", "light"]))
    assert [x.id for x in result["spell_save_actions"]] == ["sacred-flame"]
    assert [x.id for x in result["healing_actions"]] == ["cure-wounds"]
    assert [x.id for x in result["defensive_spell_actions"]] == ["bless", "sanctuary"]
    assert result["spell_save_actions"][0].dc == 12
    assert result["healing_actions"][0].healing_bonus == 2
    assert result["unbound_spell_ids"] == []
    assert result["arena_neutral_spell_ids"] == ["light"]


def test_incomplete_source_cannot_be_treated_as_certified():
    with pytest.raises(ValueError, match="incomplete"):
        prepared_spell_actions_2014(_monster(["bless"], complete=False))


def test_invalid_spell_save_dc_fails_closed():
    monster = _monster(["sacred-flame"])
    monster.spellcasting["save_dc"] = None
    with pytest.raises(ValueError, match="save DC"):
        prepared_spell_actions_2014(monster)


def test_real_acolyte_source_reuses_prepared_actions_without_admission():
    from app.content.monster_source_2014 import load_monster_source_2014
    source = next(m for m in load_monster_source_2014() if m.id == "acolyte")
    result = prepared_spell_actions_2014(source)
    expected = {spell["id"] for spell in source.spellcasting["spells"]}
    covered = {
        item.id for field in ("spell_save_actions", "healing_actions", "defensive_spell_actions")
        for item in result[field]
    }
    assert covered | set(result["unbound_spell_ids"]) | set(result["arena_neutral_spell_ids"]) == expected
    assert {"sacred-flame", "cure-wounds", "bless", "sanctuary"} <= covered
    assert result["unbound_spell_ids"] == [], "Acolyte must not be treated as spell-ready with missing effects"


def test_source_ability_abbreviation_matches_shared_monster_normalizer():
    source = _monster(["cure-wounds"])
    source.abilities = {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 14, "cha": 10}
    actions = prepared_spell_actions_2014(source)
    assert actions["healing_actions"][0].healing_bonus == 2


def test_light_is_only_arena_neutral_as_a_cantrip():
    source = _monster(["light"])
    source.spellcasting["spells"][0]["level"] = 1
    result = prepared_spell_actions_2014(source)
    assert result["arena_neutral_spell_ids"] == []
    assert result["unbound_spell_ids"] == ["light"]


def test_utility_cantrips_are_accounted_for_without_combat_effects():
    source = _monster(["light", "thaumaturgy"])
    for spell in source.spellcasting["spells"]:
        spell["level"] = 0
    result = prepared_spell_actions_2014(source)
    assert result["arena_neutral_spell_ids"] == ["light", "thaumaturgy"]
    assert result["spell_save_actions"] == []
    assert result["healing_actions"] == []
    assert result["defensive_spell_actions"] == []
