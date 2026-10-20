"""Fail-closed 2014 source binding for innate Invisible self-actions.

This compiler recognizes one exact printed source clause. All in-fight
behavior is shared with other self-buffs through the condition engine.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_PRINTED_INVISIBILITY = (
    "The sprite magically turns invisible until it attacks or casts a spell, "
    "or until its concentration ends (as if concentrating on a spell). "
    "Any equipment the sprite wears or carries is invisible with it."
)


def source_invisibility_action_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Admit only the full, unaltered 2014 action as a shared self-buff."""
    try:
        if "Invisibility" not in monster.action_names:
            return []
        printed = source_sections_2014(monster.source_actions).get("Invisibility")
        if printed is None:
            return []
        normalized = lambda value: " ".join(value.replace("’", "'").casefold().split())
        if normalized(printed) != normalized(_PRINTED_INVISIBILITY):
            return []
        return [TimedSelfBuffAction(
            id="invisibility", name="Invisibility", action_cost="action",
            condition_ids=["invisible"], magical_effect=True,
            concentration=True, ends_on_owner_attack=True,
            ends_on_owner_spell_cast=True, priority=70,
            duration_rounds=None, expiry_timing=None, animation="invisibility",
        )]
    except Exception:
        logger.exception("2014 source Invisibility binding failed for %s.", monster.id)
        raise
