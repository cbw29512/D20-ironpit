"""2014 source-only classification for effects requiring an absent control amulet.

The Iron Pit's fixed combatant roster has no external amulet wearer/controller.
Source text is preserved, and no monster-name or runtime ability dispatch occurs.
Unknown or modified source paragraphs fail closed instead of becoming inert.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_TRAIT_CLAUSES = frozenset({
    (
        "The shield guardian is magically bound to an amulet. As long as "
        "the guardian and its amulet are on the same plane of existence, "
        "the amulet's wearer can telepathically call the guardian to travel "
        "to it, and the guardian knows the distance and direction to the "
        "amulet. If the guardian is within 60 feet of the amulet's wearer, "
        "half of any damage the wearer takes (rounded up) is transferred "
        "to the guardian."
    ),
    (
        "A spellcaster who wears the shield guardian's amulet can cause "
        "the guardian to store one spell of 4th level or lower. To do so, "
        "the wearer must cast the spell on the guardian. The spell has no "
        "effect but is stored within the guardian. When commanded to do so "
        "by the wearer or when a situation arises that was predefined by "
        "the spellcaster, the guardian casts the stored spell with any "
        "parameters set by the original caster, requiring no components. "
        "When the spell is cast or a new spell is stored, any previously "
        "stored spell is lost."
    ),
})
_REACTION_CLAUSE = (
    "When a creature makes an attack against the wearer of the "
    "guardian's amulet, the guardian grants a +2 bonus to the "
    "wearer's AC if the guardian is within 5 feet of the wearer."
)


def source_proven_amulet_only_trait_2014(
    monster: SourceMonster2014, trait_name: str,
) -> bool:
    """Identity-neutral proof: complete trait outcome requires an amulet wearer."""
    try:
        if trait_name not in monster.trait_names:
            return False
        sections = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        return sections.get(trait_name, "") in _TRAIT_CLAUSES
    except Exception:
        logger.exception("Amulet trait proof failed for %s / %s", monster.id, trait_name)
        raise


def source_proven_amulet_only_reactions_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """An exact full reaction may be classified inert without a linked wearer."""
    try:
        sections = source_sections_2014(
            monster.source_reactions, include_continuations=True,
        )
        return frozenset(
            name for name in monster.reaction_names
            if sections.get(name, "") == _REACTION_CLAUSE
        )
    except Exception:
        logger.exception("Amulet reaction proof failed for %s", monster.id)
        raise
