"""Whole-clause proofs for 2014 reactions with no Iron Pit combat outcome."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_NONACTIONABLE_REACTION_CLAUSES_2014 = {
    "Shriek": (
        "When bright light or a creature is within 30 feet of the shrieker, it emits "
        "a shriek audible within 300 feet of it. The shrieker continues to shriek "
        "until the disturbance moves out of range and for 1d4 of the shrieker's "
        "turns afterward."
    ),
}


def verified_nonactionable_reaction_names_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Return printed reactions whose complete effect cannot alter Pit combat state."""
    try:
        sections = source_sections_2014(
            monster.source_reactions or "", include_continuations=True,
        )
        normalized = {
            name: " ".join(text.replace("’", "'").casefold().split())
            for name, text in sections.items()
        }
        verified: set[str] = set()
        for name in monster.reaction_names:
            expected = _NONACTIONABLE_REACTION_CLAUSES_2014.get(name)
            if expected is None:
                continue
            if normalized.get(name) == " ".join(expected.casefold().split()):
                verified.add(name)
        return frozenset(verified)
    except Exception:
        logger.exception(
            "Failed nonactionable 2014 reaction proof for %s.", monster.name
        )
        raise
