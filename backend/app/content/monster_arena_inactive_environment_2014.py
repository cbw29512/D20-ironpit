"""Source-verified, standard-arena-inactive permanent environmental traits."""
from __future__ import annotations

import logging

from app.content.monster_heated_body_2014 import fire_form_contact_retaliation_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def arena_inactive_environment_traits_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Admit only proven unreachable clauses; keep printed card traits intact."""
    try:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        accepted: set[str] = set()
        if "Fire Form" in monster.trait_names:
            clause = " ".join(sections.get("Fire Form", "").casefold().split())
            # Contact retaliation and Touch ignition remain executable separately.
            # Entering another creature's occupied square is not a legal Pit move.
            if (
                fire_form_contact_retaliation_2014(monster)
                and "first time it enters a creature's space on a turn" in clause
                and "catches fire" in clause
                and "at the start of each of its turns" in clause
                and "can enter a hostile creature's space and stop there" in clause
            ):
                accepted.add("Fire Form")
        if "Water Susceptibility" in monster.trait_names:
            clause = " ".join(sections.get("Water Susceptibility", "").casefold().split())
            if all(part in clause for part in (
                "moves in water", "gallon of water", "1 cold damage",
            )):
                # The standard arena has no water exposure source.
                # This does not certify the trait in water-enabled arenas.
                accepted.add("Water Susceptibility")
        return frozenset(accepted)
    except Exception:
        logger.exception("Failed arena-inactive environmental trait proof for %s.", monster.id)
        raise
