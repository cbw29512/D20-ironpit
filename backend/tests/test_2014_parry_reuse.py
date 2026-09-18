from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, supports_parry_reaction_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _source():
    return {monster.id: monster for monster in load_monster_source_2014()}


def test_2014_noble_reuses_universal_parry_and_becomes_basic_candidate() -> None:
    noble = _source()["noble"]
    assert noble.reaction_names == ["Parry"]
    assert noble.parry_ac_bonus == 2
    assert supports_parry_reaction_2014(noble) is True
    assert basic_blockers_2014(noble) == ()

    definition = adapt_basic_monster_2014(noble)
    assert definition.source_reaction_names == ["Parry"]
    assert definition.parry_reaction is not None
    assert definition.parry_reaction.ac_bonus == 2

    template = compile_combatant(definition)
    assert template.ruleset == "2014"
    assert template.id == "2014-noble"
    assert template.parry_reaction is not None
    assert template.parry_reaction.ac_bonus == 2


def test_other_2014_parry_monsters_only_lose_the_reaction_blocker() -> None:
    source = _source()
    for monster_id in ("bandit-captain", "knight"):
        monster = source[monster_id]
        assert monster.reaction_names == ["Parry"]
        assert monster.parry_ac_bonus == 2
        assert supports_parry_reaction_2014(monster) is True
        blockers = basic_blockers_2014(monster)
        assert "source:reaction" not in blockers
        assert blockers
