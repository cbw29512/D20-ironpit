"""2014 source-proven breathing-medium capabilities (generic physiology).

State schema: monster cards declare can_breathe_water, never an inferred habitat
or movement mode. Only full printed trait paragraphs establish the capability.
An extra trait rider fails closed without granting that medium.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_PROVEN = {
    "Amphibious": re.compile(r"The [A-Za-z][A-Za-z -]* can breathe air and water\.", re.I),
    "Water Breathing": re.compile(r"The [A-Za-z][A-Za-z -]* can breathe only underwater\.", re.I),
    "Limited Amphibiousness": re.compile(
        r"The [A-Za-z][A-Za-z -]* can breathe air and water, but it needs "
        r"to be submerged at least once every 4 hours to avoid suffocating\.", re.I,
    ),
}


def source_can_breathe_water_2014(monster: SourceMonster2014) -> bool:
    """Prove a source-owned medium independently of a monster's identity."""
    try:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        for heading, pattern in _PROVEN.items():
            if heading not in monster.trait_names:
                continue
            printed = sections.get(heading, "").lstrip(": ")
            if pattern.fullmatch(printed):
                return True
        return False
    except Exception:
        logger.exception("Failed 2014 breathing-medium source proof for %s.", monster.id)
        raise
