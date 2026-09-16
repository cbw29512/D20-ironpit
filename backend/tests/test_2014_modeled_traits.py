from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.traits import CombatTrait


_PACK_ONLY = {
    "baboon", "blood-hawk", "giant-rat", "giant-vulture", "hyena", "jackal",
    "reef-shark", "thug", "tribal-warrior", "vulture",
}
_UNDEAD_FORTITUDE = {"ogre-zombie", "zombie"}
_REUSABLE_TRAIT_IDS = _PACK_ONLY | _UNDEAD_FORTITUDE | {"raven"}


def test_existing_universal_traits_admit_2014_monsters():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in _PACK_ONLY:
        monster = source[monster_id]
        assert "Pack Tactics" in monster.trait_names
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert template.ruleset == "2014"
        assert template.id == f"2014-{monster_id}"
        assert template.source_trait_names == monster.trait_names
        assert CombatTrait.PACK_TACTICS in template.combat_traits
    for monster_id in _UNDEAD_FORTITUDE:
        monster = source[monster_id]
        assert "Undead Fortitude" in monster.trait_names
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert template.ruleset == "2014"
        assert template.id == f"2014-{monster_id}"
        assert template.source_trait_names == monster.trait_names
        assert CombatTrait.UNDEAD_FORTITUDE in template.combat_traits


def test_mimicry_is_arena_neutral_for_raven():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    raven = source["raven"]
    assert raven.trait_names == ["Mimicry"]
    assert basic_blockers_2014(raven) == ()
    template = compile_combatant(adapt_basic_monster_2014(raven))
    assert template.ruleset == "2014"
    assert template.id == "2014-raven"
    assert template.source_trait_names == ["Mimicry"]


def test_reusable_trait_batch_remains_admitted():
    ready_ids = {
        monster.id for monster in load_monster_source_2014()
        if not basic_blockers_2014(monster)
    }
    assert _REUSABLE_TRAIT_IDS <= ready_ids
