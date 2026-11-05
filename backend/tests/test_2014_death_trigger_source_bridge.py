"""2014 death-trigger source cards must compile without name dispatch."""
from __future__ import annotations

import pytest

from app.content.monster_death_trigger_saves_2014 import death_trigger_saves_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_four_source_death_damage_cards() -> None:
    try:
        by_name = {row.name: row for row in load_monster_source_2014()}
        expected = {
            "Ice Mephit": (10, 5, "slashing", "half"),
            "Magma Mephit": (11, 5, "fire", "half"),
            "Magmin": (11, 10, "fire", "half"),
            "Steam Mephit": (10, 5, "fire", "none"),
        }
        for name, values in expected.items():
            bound = death_trigger_saves_2014(by_name[name])
            assert len(bound) == 1
            action = bound[0].save_action
            assert (action.dc, action.area.radius_ft, action.damage_type, action.success_damage) == values
        assert death_trigger_saves_2014(by_name["Dust Mephit"]) == []
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Death-trigger source test failed.")
        raise
