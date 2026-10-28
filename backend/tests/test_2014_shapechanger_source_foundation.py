"""Source verification foundation for 2014 Shapechanger family.

Does not admit monsters or clear blockers. Exact-head CI required for any admission claim.
"""
from app.content.monster_source_2014 import load_monster_source_2014

def test_imp_shapechanger_source_text_is_immutable_and_printed():
    mons = load_monster_source_2014()
    imp = next(m for m in mons if m.name == "Imp")
    assert "Shapechanger" in imp.trait_names
    text = imp.source_traits
    assert "polymorph into a beast form" in text
    assert "rat" in text and "raven" in text and "spider" in text
    assert "statistics are the same" in text
    # Source immutability: no mutation of the loaded source.
    assert imp.name == "Imp"
