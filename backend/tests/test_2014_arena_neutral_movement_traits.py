from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.traits import CombatTrait

_EXPECTED = {
    "giant-wolf-spider": frozenset({"Spider Climb", "Web Sense", "Web Walker"}),
    "spider": frozenset({"Spider Climb", "Web Sense", "Web Walker"}),
    "lion": frozenset({"Running Leap"}),
    "young-white-dragon": frozenset({"Ice Walk"}),
}


def _source():
    return {monster.id: monster for monster in load_monster_source_2014()}


def test_flat_arena_traits_unlock_only_through_source_inertness() -> None:
    source = _source()
    for monster_id, neutral_traits in _EXPECTED.items():
        monster = source[monster_id]
        assert neutral_traits <= set(monster.trait_names)
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert neutral_traits <= set(template.source_trait_names)


def test_arena_neutral_traits_do_not_invent_combat_state_or_movement() -> None:
    source = _source()
    expected_modeled = {
        "giant-wolf-spider": set(),
        "spider": set(),
        "lion": {CombatTrait.PACK_TACTICS, CombatTrait.CHARGE},
        "young-white-dragon": set(),
    }
    for monster_id in _EXPECTED:
        monster = source[monster_id]
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert set(template.combat_traits) == expected_modeled[monster_id]
        assert template.movement_modes.walk_ft == int(monster.speed.get("walk", 0))
        assert template.movement_modes.climb_ft == int(monster.speed.get("climb", 0))


def test_pinned_2014_text_matches_flat_arena_classification() -> None:
    source = _source()
    assert "in contact with a web" in source["spider"].source_traits
    assert "long jump up to 25 feet" in source["lion"].source_traits
    assert "difficult terrain composed of ice or snow" in source["young-white-dragon"].source_traits
