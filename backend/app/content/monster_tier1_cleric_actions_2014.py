"""Bind one source-proven low-level Cleric spell family to shared resolvers.

No monster identity selects a behavior. Source supplies 2014 DC, Wisdom,
spell levels and slot quantities; temporary state and existing spell actions
own spending, saves, modifiers, healing and expiry.
"""
from __future__ import annotations

import logging

from app.content.cleric_2014_level1_spells import (
    bless_2014, cure_wounds_2014, sacred_flame_2014,
)
from app.content.shared_spells_2014 import sanctuary_2014
from app.content.monster_source_tier1_cleric_2014 import (
    source_proves_tier1_cleric_spells_2014,
)

logger = logging.getLogger(__name__)


def tier1_cleric_save_spells_2014(monster):
    try:
        if not source_proves_tier1_cleric_spells_2014(monster):
            return []
        return [sacred_flame_2014(int(monster.spellcasting["save_dc"]))]
    except Exception:
        logger.exception("Failed source-backed prepared Cleric cantrip binding.")
        raise


def tier1_cleric_defensive_spells_2014(monster):
    try:
        if not source_proves_tier1_cleric_spells_2014(monster):
            return []
        return [
            bless_2014(),
            sanctuary_2014(int(monster.spellcasting["save_dc"])),
        ]
    except Exception:
        logger.exception("Failed source-backed Cleric defensive spell binding.")
        raise


def tier1_cleric_healing_spells_2014(monster):
    try:
        if not source_proves_tier1_cleric_spells_2014(monster):
            return []
        wisdom = monster.abilities.get("wis")
        if type(wisdom) is not int or not 1 <= wisdom <= 30:
            raise ValueError("Source Cleric lacks a valid Wisdom score")
        wisdom_modifier = (wisdom - 10) // 2
        return [cure_wounds_2014(wisdom_modifier, 0)]
    except Exception:
        logger.exception("Failed source-backed Cleric healing spell binding.")
        raise
