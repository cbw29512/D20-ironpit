from __future__ import annotations

from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


_ARENA_GEOMETRY_ONLY = {
    "bulette": "Standing Leap",
    "frog": "Standing Leap",
    "giant-frog": "Standing Leap",
    "giant-toad": "Standing Leap",
    "black-pudding": "Amorphous",
    "gray-ooze": "Amorphous",
    "ochre-jelly": "Amorphous",
    "shadow": "Amorphous",
    "earth-elemental": "Siege Monster",
    "kraken": "Siege Monster",
    "tarrasque": "Siege Monster",
    "treant": "Siege Monster",
}


def test_arena_geometry_only_traits_remain_on_cards_but_do_not_block() -> None:
    source = {monster.id: monster for monster in load_monster_source_2014()}

    for monster_id, trait_name in _ARENA_GEOMETRY_ONLY.items():
        monster = source[monster_id]

        # Keep the printed trait on source/card data.
        assert trait_name in monster.trait_names

        # Standard Iron Pit provides no matching geometry/object target.
        assert trait_name in ARENA_NEUTRAL_TRAITS_2014
        assert trait_name not in unsupported_traits_2014(monster)
