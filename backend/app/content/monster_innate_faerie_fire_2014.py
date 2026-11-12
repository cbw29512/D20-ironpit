"""2014 innate Faerie Fire binding to the already shared Druid spell.

The card must prove its complete innate list, ability, DC and use budget;
the combat engine receives only the universal SpellSaveAction parameters.
Darkness remains independently unbound until its sight mechanics are certified.
"""
from __future__ import annotations

import logging
import re

from app.content.druid_2014_level1_spells import faerie_fire_2014
from app.content.monster_innate_source_2014 import (
    innate_spellcasting_source_2014,
    innate_spells_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)

_PRINTED = re.compile(
    r"The (?P<actor>[a-z][a-z -]*)'s (?:innate )?spellcasting ability is "
    r"(?P<ability>Wisdom|Charisma) \(spell save DC (?P<dc>\d+)\)\. "
    r"(?:The (?P=actor)|It) can innately cast the following spells, "
    r"requiring no material components: "
    r"At will: dancing lights 1/day each: darkness, faerie fire",
    re.IGNORECASE,
)
_EXPECTED = (
    ("dancing-lights", "dancing lights", "at_will", None, False, None),
    ("darkness", "darkness", "per_day", 1, False, None),
    ("faerie-fire", "faerie fire", "per_day", 1, False, None),
)


def source_proven_innate_faerie_fire_2014(
    monster: SourceMonster2014,
) -> list[SpellSaveAction]:
    """Reuse the generic 2014 Faerie Fire save without card-name dispatch."""
    try:
        source = innate_spellcasting_source_2014(monster)
        if source is None or source.get("source_complete") is not True:
            return []
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Innate Spellcasting", "")
        match = _PRINTED.fullmatch(
            " ".join(printed.replace("’", "'").split()),
        )
        if match is None:
            return []
        save_dc = int(match["dc"])
        if not (1 <= save_dc <= 40):
            return []
        if (source.get("save_dc") != save_dc
                or source.get("ability") != match["ability"].lower()):
            return []
        rows = tuple(
            (spell.get("id"), spell.get("name"), spell.get("usage"),
             spell.get("uses_per_day"), spell.get("shared_pool"),
             spell.get("qualifier"))
            for spell in innate_spells_2014(monster)
        )
        if rows != _EXPECTED:
            return []
        return [faerie_fire_2014(save_dc)]
    except Exception:
        logger.exception("2014 innate Faerie Fire source proof failed for %s.", monster.id)
        raise
