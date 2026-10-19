"""Proof obligations for 2014 non-actionable sensory and social information.

This does not apply any runtime combat rule. It certifies a printed ability
only while its complete inspected effect has no executable Iron Pit outcome.
"""

from __future__ import annotations

import logging
import re

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


def verified_nonactionable_information_2014(
    monster: SourceMonster2014, trait_name: str,
) -> bool:
    """Classify only explicitly proven printed informational traits."""
    try:
        if trait_name not in monster.trait_names:
            return False
        clauses = _INFORMATIONAL_CLAUSES.get(trait_name)
        if clauses is None:
            return False
        source_body = source_sections_2014(monster.source_traits).get(trait_name)
        if not source_body:
            return False
        normalized = source_body.casefold().replace("’", "'")
        return all(clause in normalized for clause in clauses)
    except Exception:
        logger.exception("2014 informational source proof failed for %s / %s", monster.id, trait_name)
        raise


# The full informational touch clause is verified, including the Charisma
# saving throw's *information-only* consequence and creature-type exceptions.
# No saving throw is rolled in combat because neither outcome changes combat.
_EMOTION_ALIGNMENT_INFORMATION = re.compile(
    r"the [a-z-]+ touches a creature and magically knows the creature's current emotional state\. "
    r"if the target fails a dc [0-9]+ charisma saving throw, the [a-z-]+ also knows "
    r"the creature's alignment\. celestials, fiends, and undead automatically "
    r"fail the saving throw\.",
    re.IGNORECASE,
)


def verified_nonactionable_action_2014(
    monster: SourceMonster2014, action_name: str,
) -> bool:
    """Prove a complete information-only Action without granting combat effects."""
    try:
        if action_name not in monster.action_names:
            return False
        body = source_sections_2014(monster.source_actions).get(action_name)
        if not body:
            return False
        normalized = " ".join(body.replace("’", "'").split())
        return _EMOTION_ALIGNMENT_INFORMATION.fullmatch(normalized) is not None
    except Exception:
        logger.exception(
            "2014 informational action source proof failed for %s / %s.",
            monster.id, action_name,
        )
        raise
