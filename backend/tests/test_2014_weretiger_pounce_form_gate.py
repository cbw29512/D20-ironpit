"""Source-prove form-qualified Pounce binds to existing charge primitive."""
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_source_monsters_2014


def test_weretiger_pounce_form_qualified_is_bound_when_charge_supported():
    monsters = {m.id: m for m in load_source_monsters_2014()}
    weretiger = monsters["weretiger"]
    unbound = unsupported_traits_2014(weretiger)
    assert "Pounce (Tiger or Hybrid Form Only)" not in unbound
    # Mutation: remove charge profile -> unbound again
    for attack in weretiger.attacks:
        if attack.charge_profile is not None:
            attack.charge_profile = None
    unbound_after = unsupported_traits_2014(weretiger)
    assert "Pounce (Tiger or Hybrid Form Only)" in unbound_after
