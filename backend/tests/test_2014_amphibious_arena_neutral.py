"""Source-prove 2014 Amphibious is arena-neutral under locked Pit rules."""

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_source_2014 import load_source_monsters_2014


def test_amphibious_exact_source_is_arena_neutral():
    monsters = {m.id: m for m in load_source_monsters_2014()}
    frog = monsters["frog"]
    assert "Amphibious" in frog.trait_names
    assert verified_arena_inert_trait_2014(frog, "Amphibious")
    # Mutation fails closed
    frog.source_traits = frog.source_traits.replace("breathe air and water", "breathe only air")
    assert not verified_arena_inert_trait_2014(frog, "Amphibious")


def test_amphibious_does_not_admit_other_traits():
    monsters = {m.id: m for m in load_source_monsters_2014()}
    chuul = monsters["chuul"]
    assert verified_arena_inert_trait_2014(chuul, "Amphibious")
    assert not verified_arena_inert_trait_2014(chuul, "Sense Magic")  # independent
