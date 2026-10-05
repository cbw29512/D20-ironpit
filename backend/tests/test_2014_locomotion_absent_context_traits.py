from __future__ import annotations

from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


_LOCOMOTION_OR_ABSENT_CONTEXT = {
    "earth-elemental": "Earth Glide",
    "xorn": "Treasure Sense",
    "purple-worm": "Tunneler",
    "sahuagin": "Limited Amphibiousness",
    "lemure": "Devil's Sight",
}


def test_locomotion_and_absent_context_traits_remain_on_cards_but_do_not_block() -> None:
    source = {monster.id: monster for monster in load_monster_source_2014()}

    for monster_id, trait_name in _LOCOMOTION_OR_ABSENT_CONTEXT.items():
        monster = source[monster_id]
        assert trait_name in monster.trait_names
        assert trait_name in ARENA_NEUTRAL_TRAITS_2014
        assert trait_name not in unsupported_traits_2014(monster)

    sahuagin = source["sahuagin"]
    assert "Shark Telepathy" in sahuagin.trait_names
    assert "Shark Telepathy" in ARENA_NEUTRAL_TRAITS_2014
    assert "Shark Telepathy" not in unsupported_traits_2014(sahuagin)

    xorn = source["xorn"]
    assert "Earth Glide" in xorn.trait_names
    assert "Earth Glide" not in unsupported_traits_2014(xorn)
