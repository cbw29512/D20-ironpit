"""Exact source proofs for individually approved arena-neutral trait policies.

These are source admission checks, never runtime ability-name dispatch.
Keep each approved exception separate from combat-effective equivalents.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Approved decisions #818/#819. Corrode Metal is deliberately absent: the
# Gray Ooze's distinct fight-only weapon penalty was approved in #784.
_APPROVED_CLAUSES = {
    "Iron Scent": (
        "The rust monster can pinpoint, by scent, the location of ferrous metal "
        "within 30 feet of it."
    ),
    "Rust Metal": (
        "Any nonmagical weapon made of metal that hits the rust monster corrodes. "
        "After dealing damage, the weapon takes a permanent and cumulative −1 "
        "penalty to damage rolls. If its penalty drops to −5, the weapon is "
        "destroyed. Nonmagical ammunition made of metal that hits the rust monster "
        "is destroyed after dealing damage."
    ),
}


def verified_approved_inert_trait_2014(monster: SourceMonster2014, trait_name: str) -> bool:
    """Keep the complete printed clause, but require its exact approved scope."""
    try:
        if trait_name not in monster.trait_names:
            return False
        expected = _APPROVED_CLAUSES.get(trait_name)
        if expected is None:
            return False
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get(trait_name)
        if printed is None:
            return False
        return " ".join(printed.casefold().split()) == " ".join(expected.casefold().split())
    except Exception:
        logger.exception("Approved neutral source proof failed for %s/%s.", monster.id, trait_name)
        raise
