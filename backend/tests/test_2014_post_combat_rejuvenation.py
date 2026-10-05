from __future__ import annotations

import re

from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014


_DELAYED_REJUVENATION = {
    "flameskull": "Rejuvenation",
    "guardian-naga": "Rejuvenation",
    "lich": "Rejuvenation",
    "mummy-lord": "Rejuvenation",
    "spirit-naga": "Rejuvenation",
    "lemure": "Hellish Rejuvenation",
}


def test_2014_rejuvenation_is_delayed_beyond_current_fight() -> None:
    source = {monster.id: monster for monster in load_monster_source_2014()}

    for monster_id, trait_name in _DELAYED_REJUVENATION.items():
        monster = source[monster_id]
        assert trait_name in monster.trait_names
        assert trait_name not in unsupported_traits_2014(monster)

        text = monster.source_traits or ""
        assert trait_name in text
        assert re.search(r"\b(?:hour|hours|day|days)\b", text, re.IGNORECASE), (
            monster.name,
            text,
        )
