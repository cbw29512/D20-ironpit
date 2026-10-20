"""Source-verified 2014 metallic-dragon Change Shape arena policy.

This is a *source classifier*, never a runtime dispatch on dragon names.
The Pit's approved decision makes this voluntary, unselected transformation
arena-inert for these eight printed sources until source-legal alternative
forms are independently certified. All printed card text remains unchanged.
"""
from __future__ import annotations

import logging
import re
from html import unescape

from app.content.monster_arena_action_policy_2014 import action_label_2014
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

# Content-policy allowlist from the approved 2014 metallic-dragon review.
# It is not consulted by the engine's combat-action resolver.
_APPROVED_SOURCE_IDS = frozenset({
    "adult-bronze-dragon",
    "adult-gold-dragon",
    "adult-silver-dragon",
    "ancient-brass-dragon",
    "ancient-bronze-dragon",
    "ancient-copper-dragon",
    "ancient-gold-dragon",
    "ancient-silver-dragon",
})

_REQUIRED_PRINTED_CLAUSES = (
    "magically polymorphs",
    "humanoid or beast",
    "challenge rating",
    "true form",
    "reverts to its true form",
    "statistics and capabilities",
)


def approved_inert_change_shape_2014(monster: SourceMonster2014) -> bool:
    """Exclude only source-verified, explicitly approved voluntary form actions.

    If the heading or any material clause changes, the action is blocked again
    instead of being converted into a different legal combat action.
    """
    try:
        if monster.id not in _APPROVED_SOURCE_IDS:
            return False
        if not any(action_label_2014(name) == "change shape" for name in monster.action_names):
            return False
        # The SRD prints Change Shape in TWO adjacent paragraphs: the
        # heading/transformation in the first and retained/replaced statistics
        # in an unheaded continuation. Parsing only the heading paragraph
        # incorrectly rejects all eight source cards.
        source = monster.source_actions or ""
        heading = "<strong>Change Shape.</strong>"
        if heading not in source:
            return False
        continuation = source.split(heading, 1)[1]
        # A future extra named Action must not serve as our source proof.
        continuation = continuation.split("<strong>", 1)[0]
        section = " ".join(unescape(re.sub(r"<[^>]+>", " ", continuation)).split()).casefold()
        return all(clause in section for clause in _REQUIRED_PRINTED_CLAUSES)
    except Exception:
        logger.exception("Could not validate printed 2014 Change Shape for %s", monster.id)
        raise
