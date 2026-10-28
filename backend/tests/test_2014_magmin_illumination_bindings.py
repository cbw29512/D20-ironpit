"""Source-backed Magmin illumination proof; never hide missing Touch mechanics."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014

def test_magmin_printed_illumination_is_inert_but_attack_remains_blocked():
    source = next(m for m in load_monster_source_2014() if m.id == "magmin")
    before = source.model_dump_json()
    assert verified_arena_inert_trait_2014(source, "Ignited Illumination")
    assert "Ignited Illumination" not in unsupported_traits_2014(source)
    assert "attack:incomplete" in basic_blockers_2014(source)
    assert source.model_dump_json() == before

def test_magmin_illumination_requires_unchanged_printed_source():
    source = next(m for m in load_monster_source_2014() if m.id == "magmin")
    altered = source.model_copy(update={"source_traits": (source.source_traits or "").replace(
        "<strong>Ignited Illumination.</strong>", "<strong>Missing Illumination.</strong>")})
    assert not verified_arena_inert_trait_2014(altered, "Ignited Illumination")
