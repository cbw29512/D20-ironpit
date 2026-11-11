"""Source-verified 2014 voluntary Change Shape arena policy.

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
from app.content.monster_source_sections_2014 import source_sections_2014

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

_DEVA_CHANGE_SHAPE_SOURCE = (
    "The deva magically polymorphs into a humanoid or beast that has a challenge "
    "rating equal to or less than its own, or back into its true form. It reverts "
    "to its true form if it dies. Any equipment it is wearing or carrying is "
    "absorbed or borne by the new form (the deva's choice). In a new form, the "
    "deva retains its game statistics and ability to speak, but its AC, movement "
    "modes, Strength, Dexterity, and special senses are replaced by those of the "
    "new form, and it gains any statistics and capabilities (except class "
    "features, legendary actions, and lair actions) that the new form has "
    "but that it lacks."
)


def source_proven_inert_voluntary_form_2014(monster: SourceMonster2014) -> bool:
    """Exclude only the whole printed form replacement, never a name guess."""
    try:
        if not any(action_label_2014(name) == "change shape"
                   for name in monster.action_names):
            return False
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get("Change Shape")
        return (
            printed is not None
            and " ".join(printed.replace("’", "'").split()).casefold()
            == _DEVA_CHANGE_SHAPE_SOURCE.casefold()
        )
    except Exception:
        logger.exception("Voluntary form source proof failed for %s", monster.id)
        raise


def approved_inert_change_shape_2014(monster: SourceMonster2014) -> bool:
    """Exclude only source-verified, explicitly approved voluntary form actions.

    If the heading or any material clause changes, the action is blocked again
    instead of being converted into a different legal combat action.
    """
    try:
        # Source-only arena policy, not replacement-form engine dispatch.
        if source_proven_inert_voluntary_form_2014(monster):
            return True
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
