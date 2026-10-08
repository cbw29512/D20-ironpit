from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.combatants import ResourceDefinition

logger = logging.getLogger(__name__)


def monster_spell_slot_resources_2014(
    monster: SourceMonster2014,
) -> list[ResourceDefinition]:
    """Translate complete pinned monster spell slots into generic combat resources.

    Immutable source defines counts. Existing spellcasting spends the resulting
    spell-slot-N resources in temporary fight state; this function never casts
    spells or marks a monster certified.
    """
    try:
        source = monster.spellcasting
        if source is None:
            return []
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            raise ValueError(f"{monster.name} has incomplete 2014 spellcasting source.")
        raw_slots = source.get("slots")
        if not isinstance(raw_slots, dict) or not raw_slots:
            raise ValueError(f"{monster.name} lacks structured spell-slot counts.")

        slot_counts: dict[int, int] = {}
        for raw_level, raw_count in raw_slots.items():
            if not isinstance(raw_level, str) or not raw_level.isdecimal():
                raise ValueError(f"{monster.name} has invalid spell-slot level {raw_level!r}.")
            level = int(raw_level)
            if raw_level != str(level) or not 1 <= level <= 9:
                raise ValueError(f"{monster.name} has out-of-range spell-slot level {raw_level!r}.")
            if type(raw_count) is not int or not 1 <= raw_count <= 4:
                raise ValueError(
                    f"{monster.name} has invalid level-{level} slot count {raw_count!r}."
                )
            slot_counts[level] = raw_count

        # Source descriptions remain authoritative, including cantrips and
        # spells whose combat effects are not yet supported by the engine.
        known = source.get("spells")
        if not isinstance(known, list) or not known:
            raise ValueError(f"{monster.name} has no structured prepared spell list.")
        ids: set[str] = set()
        for spell in known:
            if not isinstance(spell, dict):
                raise ValueError(f"{monster.name} has malformed prepared spell data.")
            spell_id, spell_level = spell.get("id"), spell.get("level")
            if not isinstance(spell_id, str) or not spell_id:
                raise ValueError(f"{monster.name} has a prepared spell without an id.")
            if type(spell_level) is not int or not 0 <= spell_level <= 9:
                raise ValueError(f"{monster.name} has invalid level for {spell_id}.")
            if spell_id in ids:
                raise ValueError(f"{monster.name} declares {spell_id} twice.")
            ids.add(spell_id)

        return [
            ResourceDefinition(
                id=f"spell-slot-{level}",
                name=f"Spell Slot {level}",
                max_uses=slot_counts[level],
            )
            for level in sorted(slot_counts)
        ]
    except Exception:
        logger.exception("Failed to bind 2014 spell-slot source for %s.", monster.name)
        raise
