from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.traits import CombatTrait

_ECHOLOCATION_IDS = {
    "bat",
    "giant-bat",
    "killer-whale",
    "swarm-of-bats",
}


def _source():
    return {monster.id: monster for monster in load_monster_source_2014()}


def test_echolocation_is_source_preserved_but_arena_neutral() -> None:
    source = _source()
    for monster_id in _ECHOLOCATION_IDS:
        monster = source[monster_id]
        assert "Echolocation" in monster.trait_names
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert "Echolocation" in template.source_trait_names


def test_echolocation_does_not_invent_runtime_sense_state() -> None:
    source = _source()
    for monster_id in _ECHOLOCATION_IDS:
        template = compile_combatant(adapt_basic_monster_2014(source[monster_id]))
        expected_traits = {CombatTrait.SWARM} if monster_id == "swarm-of-bats" else set()
        assert set(template.combat_traits) == expected_traits


def test_darkmantle_remains_fail_closed_for_separate_mechanics() -> None:
    darkmantle = _source()["darkmantle"]
    assert "Echolocation" in darkmantle.trait_names
    blockers = set(basic_blockers_2014(darkmantle))
    assert blockers
    assert "attack:incomplete" in blockers
