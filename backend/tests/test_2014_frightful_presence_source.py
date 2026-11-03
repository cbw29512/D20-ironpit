"""Source proof for 2014 Frightful Presence family."""
import pytest
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_frightful_presence_2014 import source_proven_frightful_presence_2014

def test_adult_black_dragon_frightful_presence_binds():
    monsters = {m.id: m for m in load_monster_source_2014()}
    dragon = monsters["adult-black-dragon"]
    bindings = source_proven_frightful_presence_2014(dragon)
    assert len(bindings) == 1
    binding = bindings[0]
    assert binding.name == "Frightful Presence"
    assert binding.dc == 16
    assert binding.range_ft == 120
    assert binding.save_ability == "wisdom"
    assert binding.failed_save_timed_effect.effect_id == "frightened"
    assert binding.failed_save_timed_effect.duration_rounds == 10

def test_unrelated_monster_has_no_binding():
    monsters = {m.id: m for m in load_monster_source_2014()}
    goblin = monsters["goblin"]
    assert source_proven_frightful_presence_2014(goblin) == []
