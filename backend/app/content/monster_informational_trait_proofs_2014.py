"""Proof obligations for 2014 non-actionable sensory and social information.

This does not apply any runtime combat rule. It certifies a printed ability
only while its complete inspected effect has no executable Iron Pit outcome.
"""

from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Exact source-derived clauses, not name-triggered runtime effects. The name
# is used exclusively to locate the printed source heading in the card.
_INFORMATIONAL_CLAUSES = {
    "Probing Telepathy": (
        "communicates telepathically with the aboleth",
        "learns the creature's greatest desires",
        "aboleth can see the creature",
    ),
    "Inscrutable": (
        "immune to any effect",
        "sense its emotions",
        "read its thoughts",
        "any divination spell",
        "that it refuses",
        "wisdom (insight) checks",
        "disadvantage",
    ),
}

# Complete printed communication-only clauses. No combat targeting, location
# reveal, action, save, damage or condition is present in any accepted body.
# Multiple source wordings share the printed trait name; each must match
# one full clause set exactly. The name only locates the heading.
_COMMUNICATION_ONLY_CLAUSE_SETS = {
    "Telepathic Bond": (
        (
            "ignores the range restriction on its telepathy",
            "communicating with a creature it has charmed",
            "don't even need to be on the same plane of existence",
        ),
        (
            "on the same plane of existence as its master",
            "magically convey what it senses to its master",
            "the two can communicate telepathically",
        ),
    ),
    "Limited Telepathy": (
        (
            "magically transmit simple messages and images",
            "any creature within 120 feet",
            "can understand a language",
            "doesn't allow the receiving creature to telepathically",
        ),
        (
            "magically communicate simple ideas, emotions, and images telepathically",
            "any creature within 100 feet",
            "can understand a language",
        ),
    ),
}


def verified_nonactionable_information_2014(
    monster: SourceMonster2014, trait_name: str,
) -> bool:
    """Classify only explicitly proven printed informational traits."""
    try:
        if trait_name not in monster.trait_names:
            return False
        source_body = source_sections_2014(monster.source_traits).get(trait_name)
        if not source_body:
            return False
        normalized = source_body.casefold().replace("’", "'")
        clauses = _INFORMATIONAL_CLAUSES.get(trait_name)
        if clauses is not None:
            return all(clause in normalized for clause in clauses)
        clause_sets = _COMMUNICATION_ONLY_CLAUSE_SETS.get(trait_name)
        if clause_sets is None:
            return False
        return any(all(clause in normalized for clause in one) for one in clause_sets)
    except Exception:
        logger.exception("2014 informational source proof failed for %s / %s", monster.id, trait_name)
        raise
