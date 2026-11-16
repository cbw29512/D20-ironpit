"""Bind printed Shield to a shared 2014 reaction-defense capability.

Only a source-complete 2014 prepared/innate spell with exact structured
Shield identity and a printed spellcasting heading is eligible.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_innate_source_2014 import innate_spellcasting_source_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.reaction_defense_spells import ReactionDefenseSpell
from app.domain.combatants import ResourceDefinition

logger = logging.getLogger(__name__)


def source_shield_reaction_2014(
    monster: SourceMonster2014,
) -> ReactionDefenseSpell | None:
    try:
        prepared = monster.spellcasting
        innate = innate_spellcasting_source_2014(monster)
        source = prepared if prepared is not None else innate
        heading = "Spellcasting" if prepared is not None else "Innate Spellcasting"
        if (
            not isinstance(source, dict)
            or source.get("source_complete") is not True
            or heading not in monster.trait_names
            or not isinstance(source.get("spells"), list)
        ):
            return None
        spell_rows = [entry for entry in source["spells"]
                      if isinstance(entry, dict) and entry.get("id") == "shield"]
        if len(spell_rows) != 1:
            return None
        entry = spell_rows[0]
        if entry.get("name") != "shield":
            return None
        if prepared is not None and (entry.get("level") != 1 or
                                     set(entry) != {"id", "name", "level"}):
            return None
        # The source heading must be present; the spell must be printed
        # after it, not merely mentioned by a different trait.
        raw = monster.source_traits or ""
        sections = re.split(
            rf"<strong>{re.escape(heading)}\.</strong>",
            raw, maxsplit=1, flags=re.I,
        )
        if len(sections) != 2:
            return None
        trailing = sections[1].split("<strong>", 1)[0]
        if re.search(r"\bshield\b", re.sub(r"<[^>]*>", " ", trailing), re.I) is None:
            return None
        if prepared is None:
            usage = entry.get("usage")
            if usage == "per_day":
                count = entry.get("uses_per_day")
                if type(count) is not int or count < 1:
                    return None
                resource_id = "shield"
            elif usage == "at_will":
                resource_id = None
            else:
                return None
        else:
            resource_id = None
        return ReactionDefenseSpell(
            id="shield", name="Shield",
            minimum_slot_level=1 if prepared is not None else None,
            resource_id=resource_id, ac_bonus=5,
            blocked_auto_hit_spell_ids=["magic-missile"],
        )
    except Exception:
        logger.exception("Failed 2014 Shield source proof for %s", monster.id)
        raise


def source_shield_reaction_resources_2014(
    monster: SourceMonster2014,
) -> list[ResourceDefinition]:
    """Create the immutable printed innate daily-use pool only when needed."""
    try:
        defense = source_shield_reaction_2014(monster)
        if defense is None or defense.resource_id is None:
            return []
        source = innate_spellcasting_source_2014(monster)
        if not isinstance(source, dict):
            raise ValueError("Innate Shield source is missing")
        entry = next(item for item in source["spells"] if item["id"] == defense.id)
        uses = entry.get("uses_per_day")
        if type(uses) is not int or uses < 1:
            raise ValueError("Innate Shield daily uses must match source")
        return [ResourceDefinition(
            id=defense.resource_id, name=defense.name, max_uses=uses,
        )]
    except Exception:
        logger.exception("Could not bind 2014 innate Shield resource for %s", monster.id)
        raise
