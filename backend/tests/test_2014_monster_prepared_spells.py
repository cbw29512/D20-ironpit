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


@pytest.mark.parametrize("spell_id,wrong_level", [
    ("sacred-flame", 1), ("bless", 0), ("cure-wounds", 0), ("sanctuary", 0),
])
def test_wrong_level_never_binds_a_combat_spell(spell_id, wrong_level):
    monster = _monster([spell_id])
    monster.spellcasting["spells"][0]["level"] = wrong_level
    result = prepared_spell_actions_2014(monster)
    assert result["unbound_spell_ids"] == [spell_id]
    assert result["spell_save_actions"] == []
    assert result["healing_actions"] == []
    assert result["defensive_spell_actions"] == []


@pytest.mark.parametrize("bad_level", [None, True, -1, 10, "1"])
def test_malformed_prepared_spell_level_fails_closed(bad_level):
    monster = _monster(["bless"])
    monster.spellcasting["spells"][0]["level"] = bad_level
    with pytest.raises(ValueError, match="invalid prepared spell level"):
        prepared_spell_actions_2014(monster)


def test_all_pinned_prepared_casters_account_for_every_source_spell_without_mutation():
    from app.content.monster_source_2014 import load_monster_source_2014
    casters = [m for m in load_monster_source_2014() if m.spellcasting]
    assert len(casters) == 13
    for monster in casters:
        original = monster.model_dump(mode="json")
        result = prepared_spell_actions_2014(monster)
        actual = [
            action.id for category in ("spell_save_actions", "healing_actions", "defensive_spell_actions")
            for action in result[category]
        ] + result["arena_neutral_spell_ids"] + result["unbound_spell_ids"]
        expected = [entry["id"] for entry in monster.spellcasting["spells"]]
        assert sorted(actual) == sorted(expected), monster.name
        assert monster.model_dump(mode="json") == original, monster.name


def test_acolyte_admitted_via_shared_prepared_spells_and_immutable_source():
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.content.monster_source_2014 import load_monster_source_2014
    source = next(m for m in load_monster_source_2014() if m.id == "acolyte")
    before = source.model_dump(mode="json")
    assert basic_blockers_2014(source) == ()
    definition = adapt_basic_monster_2014(source)
    assert {action.id for action in definition.spell_save_actions} >= {"sacred-flame"}
    assert {action.id for action in definition.healing_actions} >= {"cure-wounds"}
    assert {action.id for action in definition.defensive_spell_actions} >= {"bless", "sanctuary"}
    assert any(resource.id == "spell-slot-1" for resource in definition.resources)
    assert source.model_dump(mode="json") == before


def test_acolyte_serializes_existing_spell_actions_for_browser():
    from app.content.monster_source_2014 import load_monster_source_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.content.capability_compiler import compile_combatant
    from scripts.browser_template_serializer import template_row

    source = next(m for m in load_monster_source_2014() if m.id == "acolyte")
    template = compile_combatant(adapt_basic_monster_2014(source))
    row = template_row(template)
    assert row["id"] == "2014-acolyte"
    assert "sacred-flame" in {action["id"] for action in row["spell_save_actions"]}
    assert "cure-wounds" in {action["id"] for action in row["healingActions"]}
    assert {"bless", "sanctuary"} <= {
        action["id"] for action in row["defensive_spell_actions"]
    }
    assert row["resources"]["spell-slot-1"] == source.spellcasting["slots"]["1"]
