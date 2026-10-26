"""Exact-source arena policy for object-only equipment corrosion Actions.

A printed Action that only changes nonmagical items is not a creature attack,
buff or save in the standard Iron Pit: no mutable equipment objects exist.
This source proof cannot clear an Action with any additional combat effect.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_OBJECT_ONLY_CORROSION = re.compile(
    r"The (?P<actor>[\\w -]+) corrodes a nonmagical ferrous metal object "
    r"it can see within (?P<reach>\\d+) feet of it\\. "
    r"If the object isn't being worn or carried, the touch destroys a "
    r"1-foot cube of it\\. "
    r"If the object is being worn or carried by a creature, the creature "
    r"can make a DC (?P<dc>\\d+) Dexterity saving throw to avoid the "
    r"(?P=actor)'s touch\\. "
    r"If the object touched is either metal armor or a metal shield being "
    r"worn or carried, it takes a permanent and cumulative −1 penalty "
    r"to the AC it offers\\. "
    r"Armor reduced to an AC of 10 or a shield that drops to a \\+0 bonus "
    r"is destroyed\\. "
    r"If the object touched is a held metal weapon, it rusts as described "
    r"in the Rust Metal trait\\.",
    re.IGNORECASE,
)


def verified_arena_inert_equipment_action_2014(
    monster: SourceMonster2014, action_name: str,
) -> bool:
    """Prove every printed effect targets gear, never creature combat state."""
    try:
        if action_name not in monster.action_names:
            return False
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(action_name)
        if printed is None:
            return False
        match = _OBJECT_ONLY_CORROSION.fullmatch(printed)
        if match is None:
            return False
        return (
            match["actor"].casefold() == monster.name.casefold()
            and 0 < int(match["reach"]) <= 30
            and 1 <= int(match["dc"]) <= 40
        )
    except Exception:
        logger.exception(
            "Failed 2014 equipment-only Action proof for %s / %s.",
            monster.id, action_name,
        )
        raise
