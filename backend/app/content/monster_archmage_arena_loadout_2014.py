from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.shared_damage_spells_2014 import finger_of_death_spell_2014
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)

_REQUIRED_SPELL_LEVELS = {
    "teleport": 7,
    "time-stop": 9,
}


def source_proven_archmage_arena_finger_of_death_2014(
    monster: SourceMonster2014,
) -> SpellSaveAction | None:
    """Bind the approved level-7 arena substitution without mutating source.

    Selection is semantic: a complete prepared-spell card must expose the exact
    18th-level Intelligence/DC 17 profile, the printed level-7 Teleport and
    level-9 Time Stop choices, and one level-7 slot. Identity is irrelevant.
    Unknown or changed source fails closed.
    """
    try:
        source = monster.spellcasting
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return None
        if (
            source.get("caster_level") != 18
            or source.get("ability") != "intelligence"
            or source.get("save_dc") != 17
            or source.get("attack_bonus") != 9
        ):
            return None
        slots = source.get("slots")
        if not isinstance(slots, dict) or slots.get("7") != 1:
            return None
        spells = source.get("spells")
        if not isinstance(spells, list):
            return None
        levels = {
            str(item.get("id")): item.get("level")
            for item in spells
            if isinstance(item, dict)
        }
        if any(levels.get(spell_id) != level for spell_id, level in _REQUIRED_SPELL_LEVELS.items()):
            return None
        if "finger-of-death" in levels:
            return None
        return finger_of_death_spell_2014(17)
    except Exception:
        logger.exception("Failed to bind source-proven 2014 arena Finger of Death.")
        raise

