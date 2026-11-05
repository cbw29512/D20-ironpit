from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014, basic_blockers_2014

def test_weretiger_pounce_trait_bound_by_existing_charge_profile():
    monsters = {m.id: m for m in load_monster_source_2014()}
    wt = monsters["weretiger"]
    assert "Pounce (Tiger or Hybrid Form Only)" in wt.trait_names
    assert unsupported_traits_2014(wt) == ()
    assert "source:trait" not in basic_blockers_2014(wt)

def test_charge_trait_name_mutation_fails_closed():
    monsters = {m.id: m for m in load_monster_source_2014()}
    wt = monsters["weretiger"]
    # Simulate source drift: rename the trait so it no longer matches base
    mutated = wt.model_copy(update={"trait_names": ["Pounce-Something-Else"] + [n for n in wt.trait_names if not n.startswith("Pounce")]})
    assert "Pounce-Something-Else" in unsupported_traits_2014(mutated)
