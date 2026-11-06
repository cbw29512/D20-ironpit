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


# Independent complete printed form: invisibility includes the owner's light
# rather than gear, and ends on the source-named non-spell Bonus Action.
_LIGHT_INVISIBILITY = re.compile(
    r"^The (?P<owner>[a-z][a-z'\-]*) and its light magically become invisible "
    r"until it attacks or uses its (?P<action>[A-Z][a-zA-Z ]+), or until its "
    r"concentration ends \(as if concentrating on a spell\)\.$",
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
        normalized = " ".join(printed.replace("’", "'").split())
        match = _PRINTED_INVISIBILITY.fullmatch(normalized)
        light_match = _LIGHT_INVISIBILITY.fullmatch(normalized) if match is None else None
        if match is None and light_match is None:
            return []
        named = match or light_match
        named_action = named.group("action")
        action_ids = (
            [re.sub(r"\s+", "-", named_action.strip().casefold())]
            if named_action else []
        )
        return [TimedSelfBuffAction(
            id="invisibility", name="Invisibility", action_cost="action",
            condition_ids=["invisible"], magical_effect=True,
            concentration=True, ends_on_owner_attack=True,
            ends_on_owner_spell_cast=(match is not None and match.group("spell") == " or casts a spell"),
            ends_on_owner_action_ids=action_ids, priority=70,
            duration_rounds=None, expiry_timing=None, animation="invisibility",
        )]
    except Exception:
        logger.exception("2014 source Invisibility binding failed for %s.", monster.id)
        raise
