"""Source-proven creature-space passage for fluid-form monsters.

Only the shared movement rule is executable. The Pit's one-creature-per-square
policy prevents ending movement in another creature's cell; its feature-free
arena also has no one-inch gaps. Printed source text remains intact on the card.
"""
from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

# These are ability labels used only to find and preserve the printed clause.
_FLUID_FORM_LABELS = frozenset({"Air Form", "Water Form"})
_PASSAGE_CLAUSE = (
    "the elemental can enter a hostile creature's space and stop there. "
    "it can move through a space as narrow as 1 inch wide without squeezing."
)


def source_proven_fluid_form_passage_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Require the entire isolated source clause, with no extra combat riders."""
    sections = source_sections_2014(monster.source_traits, include_continuations=True)
    bound = set()
    for label in _FLUID_FORM_LABELS.intersection(monster.trait_names):
        printed = sections.get(label)
        if printed is None:
            continue
        normalized = " ".join(
            printed.casefold().replace("’", "'").replace(" ", " ").split()
        )
        if normalized == _PASSAGE_CLAUSE:
            bound.add(label)
    return frozenset(bound)
