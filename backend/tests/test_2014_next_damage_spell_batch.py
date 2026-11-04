"""Next 2014 damage-spell batch: highest remaining damage first.

Disintegrate, Finger of Death, Cloudkill, Blight, Ice Storm, Thunderwave, Sacred Flame.
Shared builders only. No new resolvers. Bound on both innate and prepared paths.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_prepared_spells_2014 import prepared_spell_save_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.shared_damage_spells_2014 import (
    blight_2014, cloudkill_2014, disintegrate_2014, finger_of_death_2014,
    ice_storm_2014, sacred_flame_2014, thunderwave_2014,
)

logger = logging.getLogger(__name__)


def test_shared_builders_construct():
    try:
        assert disintegrate_2014(15).id == "disintegrate"
        assert finger_of_death_2014(15).id == "finger-of-death"
        assert blight_2014(15).id == "blight"
        assert cloudkill_2014(15).id == "cloudkill"
        assert ice_storm_2014(15).id == "ice-storm"
        assert thunderwave_2014(15).id == "thunderwave"
        assert sacred_flame_2014(15).id == "sacred-flame"
    except Exception:
        logger.exception("Shared damage builders failed")
        raise


def test_prepared_and_innate_bind_new_spells_when_printed():
    try:
        monsters = {m.id: m for m in load_monster_source_2014()}
        # Spot-check a couple of known casters if present
        for mid, action_id in (("archmage", "lightning-bolt"), ("acolyte", "sacred-flame")):
            m = monsters.get(mid)
            if m is None:
                continue
            prepared = {a.id for a in prepared_spell_save_actions_2014(m)}
            innate = {a.id for a in innate_spell_save_actions_2014(m)}
            # At least one path should bind the printed spell if it is on the card
            printed = set()
            if m.spellcasting and isinstance(m.spellcasting, dict):
                printed.update(s.get("id") for s in (m.spellcasting.get("spells") or []) if isinstance(s, dict))
            if m.innate_spellcasting and isinstance(m.innate_spellcasting, dict):
                printed.update(s.get("id") for s in (m.innate_spellcasting.get("spells") or []) if isinstance(s, dict))
            if action_id in printed:
                assert action_id in prepared or action_id in innate
    except Exception:
        logger.exception("Binder wiring check failed")
        raise
