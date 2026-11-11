"""Source-verified hostile-space overlap permission for 2014 creature forms.

The printed trait name is a display label, not a combat resolver switch.
Only an entire matching source section can grant the universal movement flag.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_fire_form_entry_2014 import fire_form_space_entry_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_HOSTILE_OVERLAP_SOURCE = (
    "the elemental can enter a hostile creature's space and stop there. "
    "it can move through a space as narrow as 1 inch wide without squeezing."
)


def source_proven_hostile_overlap_traits_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Bind exactly proven movement-only clauses; reject other unknown riders."""
    try:
        sections = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        return frozenset(
            name for name in monster.trait_names
            if " ".join(sections.get(name, "").casefold().replace("’", "'").split())
            == _HOSTILE_OVERLAP_SOURCE
            or (name == "Fire Form" and fire_form_space_entry_2014(monster) is not None)
        )
    except Exception:
        logger.exception(
            "Failed hostile-space source proof for %s.", monster.id,
        )
        raise


def source_allows_hostile_overlap_2014(monster: SourceMonster2014) -> bool:
    """Compile the generic form's source-owned overlap flag."""
    try:
        return bool(source_proven_hostile_overlap_traits_2014(monster))
    except Exception:
        logger.exception("Failed hostile-space compilation for %s.", monster.id)
        raise
