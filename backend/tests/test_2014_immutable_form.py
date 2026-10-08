from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


_IMMUTABLE_FORM_IDS = ("clay-golem", "flesh-golem", "iron-golem", "stone-golem")
_NEWLY_READY_IDS = ("iron-golem", "stone-golem")
_STILL_BLOCKED_IDS = ("clay-golem", "flesh-golem")


def _source():
    return {monster.id: monster for monster in load_monster_source_2014()}


def test_immutable_form_is_arena_neutral_for_exact_2014_source_family() -> None:
    source = _source()

    assert "Immutable Form" in ARENA_NEUTRAL_TRAITS_2014
    actual = {
        monster.id for monster in source.values()
        if "Immutable Form" in monster.trait_names
    }
    assert actual == set(_IMMUTABLE_FORM_IDS)

    for monster_id in _IMMUTABLE_FORM_IDS:
        monster = source[monster_id]
        assert "Immutable Form" in monster.trait_names
        assert "Immutable Form" not in unsupported_traits_2014(monster)


def test_immutable_form_unlocks_only_the_two_single_blocker_golems() -> None:
    source = _source()

    for monster_id in _NEWLY_READY_IDS:
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert "Immutable Form" in template.source_trait_names

    for monster_id in _STILL_BLOCKED_IDS:
        blockers = basic_blockers_2014(source[monster_id])
        assert blockers
        assert "source:trait" not in blockers
