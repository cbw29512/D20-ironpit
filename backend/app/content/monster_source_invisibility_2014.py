"""Fail-closed 2014 source binding for innate Invisible self-actions.

This compiler recognizes one exact printed source clause. All in-fight
behavior is shared with other self-buffs through the condition engine.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

# Source-declared exit predicates. Attack ends both patterns; spell cast
# ends only those whose complete printed clause explicitly says so.
# Backreference confirms the equipment sentence names the same source.
_PRINTED_INVISIBILITY = re.compile(
    r"^The (?P<owner>[a-z][a-z'-]*) magically turns invisible until it attacks"
    r"(?P<spell> or casts a spell| or uses (?P<action>[A-Z][a-zA-Z ]*))?,? or until its concentration ends"
    r" \(as if concentrating on a spell\)\. Any equipment the (?P=owner) wears"
    r" or carries is invisible with it\.$",
    re.IGNORECASE,
)


def source_invisibility_action_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Admit only the full, unaltered 2014 action as a shared self-buff."""
    try:
        if "Invisibility" not in monster.action_names:
            return []
        printed = source_sections_2014(monster.source_actions).get("Invisibility")
        if printed is None:
            return []
        match = _PRINTED_INVISIBILITY.fullmatch(" ".join(printed.replace("’", "'").split()))
        if match is None:
            return []
        if match.group("action") is not None:
            # A named-action exit requires the shared runtime event listener;
            # retain the source blocker until that generic capability exists.
            return []
        return [TimedSelfBuffAction(
            id="invisibility", name="Invisibility", action_cost="action",
            condition_ids=["invisible"], magical_effect=True,
            concentration=True, ends_on_owner_attack=True,
            ends_on_owner_spell_cast=match.group("spell") is not None, priority=70,
            duration_rounds=None, expiry_timing=None, animation="invisibility",
        )]
    except Exception:
        logger.exception("2014 source Invisibility binding failed for %s.", monster.id)
        raise
