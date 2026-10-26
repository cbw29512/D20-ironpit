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

def test_source_verified_hydra_enters_real_compiled_2014_roster():
    """The same universal head profile must reach the fight card unchanged."""
    import logging

    from app.content.capability_compiler import compile_combatant
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014

    logger = logging.getLogger(__name__)
    try:
        source = next(m for m in load_monster_source_2014() if m.id == "hydra")
        snapshot = source.model_dump_json()
        assert basic_blockers_2014(source) == ()
        template = compile_combatant(adapt_basic_monster_2014(source))
        profile = template.variable_heads
        assert profile is not None
        assert profile.initial_heads == 5
        assert profile.sever_damage_threshold == 25
        assert profile.heads_per_regrowth == 2
        assert profile.healing_per_regrown_head == 10
        assert profile.regrowth_blocking_damage_types == ["fire"]
        assert source.model_dump_json() == snapshot
    except Exception:
        logger.exception("Hydra real-card admission proof failed.")
        raise
