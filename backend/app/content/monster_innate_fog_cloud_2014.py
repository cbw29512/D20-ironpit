"""2014 Fog Cloud source proof using the shared physical-obscuration zone.

Spell rules are card data; the Python/browser zone engine resolves all sight,
Concentration, placement, resource, and expiry behavior. Source monster names
never dispatch combat effects.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_source_2014 import (
    innate_spellcasting_source_2014,
    innate_spells_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.suppression_zones import PersistentSuppressionZoneAction

logger = logging.getLogger(__name__)

# Exact normalized 2014 source clauses, not monster-name exceptions.
_ICE_CLAUSE = (
    "(1/day). the mephit can innately cast fog cloud, requiring no material "
    "components. its innate spellcasting ability is charisma."
)
_GIANT_CLAUSE = (
    "the giant's innate spellcasting ability is charisma. it can innately "
    "cast the following spells, requiring no material components: "
    "at will: detect magic, fog cloud, light "
    "3/day each: feather fall, fly, misty step, telekinesis "
    "1/day each: control weather, gaseous form"
)
_ICE_SPELLS = (
    ("fog-cloud", "fog cloud", "per_day", 1, False, None),
)
_GIANT_SPELLS = (
    ("detect-magic", "detect magic", "at_will", None, False, None),
    ("fog-cloud", "fog cloud", "at_will", None, False, None),
    ("light", "light", "at_will", None, False, None),
    ("feather-fall", "feather fall", "per_day", 3, False, None),
    ("fly", "fly", "per_day", 3, False, None),
    ("misty-step", "misty step", "per_day", 3, False, None),
    ("telekinesis", "telekinesis", "per_day", 3, False, None),
    ("control-weather", "control weather", "per_day", 1, False, None),
    ("gaseous-form", "gaseous form", "per_day", 1, False, None),
)


def source_proven_innate_fog_cloud_2014(
    monster: SourceMonster2014,
) -> list[PersistentSuppressionZoneAction]:
    """Attach Fog Cloud only when the full source and parsed spell list agree."""
    try:
        source = innate_spellcasting_source_2014(monster)
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return []
        if source.get("ability") != "charisma" or source.get("unsupported_text"):
            return []

        sections = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        printed = (
            sections.get("Innate Spellcasting (1/Day)")
            or sections.get("Innate Spellcasting")
            or ""
        ).replace("’", "'")
        printed = " ".join(printed.casefold().split())
        rows = tuple(
            (item.get("id"), item.get("name"), item.get("usage"),
             item.get("uses_per_day"), item.get("shared_pool"),
             item.get("qualifier"))
            for item in innate_spells_2014(monster)
        )
        if printed == _ICE_CLAUSE and rows == _ICE_SPELLS:
            resource_id = "fog-cloud"
        elif printed == _GIANT_CLAUSE and rows == _GIANT_SPELLS:
            resource_id = None
        else:
            return []

        return [PersistentSuppressionZoneAction(
            id="fog-cloud", name="Fog Cloud", level=1, action_cost="action",
            cast_range_ft=120, radius_ft=20, duration_rounds=600,
            concentration=True, deafens=False, blocks_verbal_spells=False,
            thunder_immunity=False, obscuration_kind="heavy-physical",
            resource_id=resource_id, resource_cost=1,
            expends_spell_slot=False, animation="fog-cloud",
            source="D&D Basic Rules 2014: Fog Cloud",
        )]
    except Exception:
        logger.exception("2014 innate Fog Cloud proof failed for %s.", monster.id)
        raise
