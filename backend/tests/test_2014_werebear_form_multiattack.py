import pytest
from app.content.monster_source_2014 import load_source_monster_2014
from app.content.monster_multiattack_2014 import multiattack_blockers_2014, multiattack_2014

def test_werebear_form_multiattack_clears_complex():
    monster = load_source_monster_2014("werebear")
    blockers = multiattack_blockers_2014(monster)
    assert "multiattack:complex" not in blockers
    cap = multiattack_2014(monster)
    assert cap is not None
    assert len(cap.variants) == 2
    bear = next(v for v in cap.variants if "bear" in v.id)
    human = next(v for v in cap.variants if "humanoid" in v.id)
    assert all(len(slot.attack_ids) == 1 for slot in bear.slots)
    assert "claw" in bear.slots[0].attack_ids[0]
    assert "greataxe" in human.slots[0].attack_ids[0]

def test_werebear_mutation_fails_closed():
    monster = load_source_monster_2014("werebear")
    original = monster.source_actions
    monster.source_actions = original.replace("two claw attacks", "three claw attacks")
    blockers = multiattack_blockers_2014(monster)
    assert "multiattack:complex" in blockers
