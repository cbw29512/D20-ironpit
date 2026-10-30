from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.traits import CombatTrait


_ARENA_NEUTRAL_IDS = {
    "awakened-shrub": "False Appearance",
    "awakened-tree": "False Appearance",
    "giant-fire-beetle": "Illumination",
    "flying-snake": "Flyby",
    "giant-owl": "Flyby",
    "mule": "Beast of Burden",
    "owl": "Flyby",
    "pteranodon": "Flyby",
    "twig-blight": "False Appearance",
}


def test_established_arena_neutral_traits_admit_exact_source_monsters():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id, trait_name in _ARENA_NEUTRAL_IDS.items():
        monster = source[monster_id]
        assert trait_name in monster.trait_names
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert template.ruleset == "2014"
        assert template.id == f"2014-{monster_id}"
        assert template.source_trait_names == monster.trait_names
        if monster_id == "mule":
            assert template.combat_traits == [CombatTrait.SURE_FOOTED]
        else:
            assert template.combat_traits == []


def test_arena_neutral_trait_batch_remains_admitted():
    ready_ids = {
        monster.id for monster in load_monster_source_2014()
        if not basic_blockers_2014(monster)
    }
    assert set(_ARENA_NEUTRAL_IDS) <= ready_ids


def test_vampire_weaknesses_are_arena_neutral():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in ("vampire", "vampire-spawn"):
        monster = source[monster_id]
        assert "Vampire Weaknesses" in monster.trait_names
        assert "Vampire Weaknesses" not in unsupported_traits_2014(monster)


def test_vampire_weaknesses_source_mutations_fail_closed():
    """A source edit cannot turn an unsupported environmental clause into admission."""
    from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014

    source = {monster.id: monster for monster in load_monster_source_2014()}
    for monster_id in ("vampire", "vampire-spawn"):
        monster = source[monster_id]
        printed = monster.source_traits or ""
        assert verified_arena_inert_trait_2014(monster, "Vampire Weaknesses")
        for required_clause in ("sunlight", "running water", "residence"):
            assert required_clause in printed.casefold()
            import re
            changed = re.sub(required_clause, "removed environmental clause", printed, flags=re.IGNORECASE)
            mutated = monster.model_copy(update={"source_traits": changed})
            assert not verified_arena_inert_trait_2014(mutated, "Vampire Weaknesses"), (
                f"{monster_id} incorrectly accepted source missing {required_clause}"
            )
