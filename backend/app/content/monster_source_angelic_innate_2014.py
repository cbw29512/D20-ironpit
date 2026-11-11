"""Exact 2014 innate-source audit of environmental and wall-only magic.

The original card stays immutable. Environmental exclusions do not acquire
combat Actions; all damage and buff spells still require shared bindings.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_innate_source_2014 import (
    innate_spellcasting_source_2014, innate_spells_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_PRINTED = re.compile(
    r"The (?P<actor>[a-z][a-z -]*)'s spellcasting ability is Charisma "
    r"\(spell save DC (?P<dc>\d+)\)\. The (?P=actor) can innately cast "
    r"the following spells, requiring no material components: "
    r"At will: detect evil and good, invisibility \(self only\) "
    r"3/day each: blade barrier, dispel evil and good, flame strike, raise dead "
    r"1/day each: commune, control weather, insect plague",
    re.IGNORECASE,
)
_EXPECTED = (
    ("detect-evil-and-good", "detect evil and good", "at_will", None, False, None),
    ("invisibility", "invisibility", "at_will", None, False, "self only"),
    ("blade-barrier", "blade barrier", "per_day", 3, False, None),
    ("dispel-evil-and-good", "dispel evil and good", "per_day", 3, False, None),
    ("flame-strike", "flame strike", "per_day", 3, False, None),
    ("raise-dead", "raise dead", "per_day", 3, False, None),
    ("commune", "commune", "per_day", 1, False, None),
    ("control-weather", "control weather", "per_day", 1, False, None),
    ("insect-plague", "insect plague", "per_day", 1, False, None),
)
# A constructed blade wall cannot be cast under the locked global Pit rule.
# Control Weather has a ten-minute cast and cannot affect this short match.
_INERT = frozenset({"blade-barrier", "control-weather"})


def source_proven_angelic_arena_exclusions_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Exclude only a fully validated printed list, never a name alone."""
    try:
        card = innate_spellcasting_source_2014(monster)
        if card is None or card.get("source_complete") is not True:
            return frozenset()
        if card.get("ability") != "charisma" or card.get("save_dc") != 20:
            return frozenset()
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Innate Spellcasting", "")
        source_text = " ".join(printed.replace("’", "'").split())
        match = _PRINTED.fullmatch(source_text)
        if match is None or int(match["dc"]) != card["save_dc"]:
            return frozenset()
        spells = tuple(
            (row.get("id"), row.get("name"), row.get("usage"),
             row.get("uses_per_day"), row.get("shared_pool"), row.get("qualifier"))
            for row in innate_spells_2014(monster)
        )
        return _INERT if spells == _EXPECTED else frozenset()
    except Exception:
        logger.exception("2014 innate environmental source audit failed for %s.", monster.id)
        raise
