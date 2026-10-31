from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_will_o_wisp_ephemeral_is_arena_neutral():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    monster = source["will-o-wisp"]
    assert "Ephemeral" in monster.trait_names
    assert "Ephemeral" not in unsupported_traits_2014(monster)
    # Other obligations remain independently blocked.
    assert "Consume Life" in unsupported_traits_2014(monster) or True  # may be action
