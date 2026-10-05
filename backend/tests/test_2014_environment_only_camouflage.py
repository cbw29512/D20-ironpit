from __future__ import annotations

from app.content.monster_arena_neutral_traits_2014 import ARENA_NEUTRAL_TRAITS_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


_ENVIRONMENT_ONLY_CAMOUFLAGE = {
    "deep-gnome-svirfneblin": "Stone Camouflage",
    "grick": "Stone Camouflage",
    "grimlock": "Stone Camouflage",
    "stone-giant": "Stone Camouflage",
    "xorn": "Stone Camouflage",
    "giant-octopus": "Underwater Camouflage",
    "octopus": "Underwater Camouflage",
}


def test_environment_only_camouflage_stays_on_source_cards_but_does_not_block() -> None:
    source = {monster.id: monster for monster in load_monster_source_2014()}

    for monster_id, trait_name in _ENVIRONMENT_ONLY_CAMOUFLAGE.items():
        monster = source[monster_id]
        assert trait_name in monster.trait_names
        assert trait_name in ARENA_NEUTRAL_TRAITS_2014
        assert trait_name not in unsupported_traits_2014(monster)
