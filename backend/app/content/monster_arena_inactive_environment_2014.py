"""Source-verified, standard-arena-inactive permanent environmental traits."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def arena_inactive_environment_traits_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Admit only proven unreachable clauses; keep printed card traits intact."""
    try:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        accepted: set[str] = set()
        if "Water Susceptibility" in monster.trait_names:
            clause = " ".join(sections.get("Water Susceptibility", "").casefold().split())
            # Exact source proof: a changed exposure distance, water quantity,
            # damage amount, or added clause must not silently pass admission.
            expected = (
                "for every 5 feet the elemental moves in water, or for every "
                "gallon of water splashed on it, it takes 1 cold damage."
            )
            if clause == expected:
                # The standard arena has no water exposure source.
                # This does not certify the trait in water-enabled arenas.
                accepted.add("Water Susceptibility")
        return frozenset(accepted)
    except Exception:
        logger.exception("Failed arena-inactive environmental trait proof for %s.", monster.id)
        raise
