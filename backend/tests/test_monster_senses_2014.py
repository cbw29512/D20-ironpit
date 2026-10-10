from __future__ import annotations
import pytest
from app.content.monster_senses_2014 import special_senses_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters

def test_source_bound_ranges_present_in_real_2014_certified_templates():
    source = {m.id: m for m in load_monster_source_2014()}
    roster = {m.id: m for m in build_basic_2014_monsters()}
    assert special_senses_2014(source["giant-scorpion"]) == (60, 0)
    assert special_senses_2014(source["half-red-dragon-veteran"]) == (10, 0)
    assert roster["2014-giant-scorpion"].blindsight_ft == 60
    assert roster["2014-half-red-dragon-veteran"].blindsight_ft == 10
    assert source["deva"].senses.startswith("Darkvision")
    assert special_senses_2014(source["deva"]) == (0, 0)

def test_pinned_2014_sight_source_entire_corpus():
    source = load_monster_source_2014()
    assert len(source) == 327
    for monster in source:
        blind, true = special_senses_2014(monster)
        assert 0 <= blind <= 1000 and 0 <= true <= 1000
        if monster.id != "twig-blight":
            if "blindsight" in monster.senses.lower():
                assert blind > 0, monster.id
            if "truesight" in monster.senses.lower():
                assert true > 0, monster.id
    # Cannot treat Twig Blight's "blind beyond" as full normal vision.
    twig = next(m for m in source if m.id == "twig-blight")
    assert special_senses_2014(twig) == (0, 0)

def test_unsupported_printed_sight_fails_closed():
    scorpion = next(m for m in load_monster_source_2014() if m.id == "giant-scorpion")
    for senses in ("Blindsight sixty ft.", "Truesight unknown", "Blindsight 9999 ft."):
        with pytest.raises(ValueError):
            special_senses_2014(scorpion.model_copy(update={"senses": senses}))
