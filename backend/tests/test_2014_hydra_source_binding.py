"""2014 Hydra binding must compile using the immutable printed source text."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_variable_heads_2014 import variable_head_profile_2014, variable_head_trait_names_2014


def test_hydra_source_heads_bind_to_existing_generic_lifecycle():
    hydra = next(monster for monster in load_monster_source_2014() if monster.id == "hydra")
    profile = variable_head_profile_2014(hydra)
    assert profile is not None
    assert profile.initial_heads == 5
    assert profile.sever_damage_threshold == 25
    assert profile.heads_per_regrowth == 2
    assert profile.healing_per_regrown_head == 10
    assert "fire" in profile.regrowth_blocking_damage_types
    assert variable_head_trait_names_2014(hydra) == {
        "Multiple Heads", "Reactive Heads",
    }
