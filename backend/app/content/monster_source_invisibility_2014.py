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
from app.domain.combatants import ResourceDefinition

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
_REST_INVISIBILITY = re.compile(
    r"^The (?P<owner>[a-z][a-z'-]*) magically turns invisible "
    r"until it attacks, casts a spell, or uses its (?P<action>[A-Za-z][a-zA-Z ]+), "
    r"or until its concentration is broken, up to (?P<hours>\d+) hour(?:s)? "
    r"\(as if concentrating on a spell\)\. Any equipment the (?P=owner) "
    r"wears or carries is invisible with it\.$", re.IGNORECASE,
)
_REST_HEADING = "Invisibility (Recharges after a Short or Long Rest)"

_LIGHT_INVISIBILITY = re.compile(
    r"^The (?P<owner>[a-z][a-z'\-]*) and its light magically become invisible "
    r"until it attacks or uses its (?P<action>[A-Z][a-zA-Z ]+), or until its "
    r"concentration ends \(as if concentrating on a spell\)\.$",
    re.IGNORECASE,
)


def source_invisibility_action_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Admit only the full, unaltered 2014 action as a shared self-buff."""
    try:
        headings = tuple(name for name in monster.action_names
                         if name in {"Invisibility", _REST_HEADING})
        if len(headings) != 1:
            return []
        heading = headings[0]
        printed = source_sections_2014(monster.source_actions).get(heading)
        if printed is None:
            return []
        normalized = " ".join(printed.replace("’", "'").split())
        match = _PRINTED_INVISIBILITY.fullmatch(normalized) if heading == "Invisibility" else None
        light_match = _LIGHT_INVISIBILITY.fullmatch(normalized) if heading == "Invisibility" else None
        rest_match = _REST_INVISIBILITY.fullmatch(normalized) if heading == _REST_HEADING else None
        if match is None and light_match is None and rest_match is None:
            return []
        named = match or light_match or rest_match
        assert named is not None
        named_action = named.group("action")
        if rest_match is not None:
            if int(rest_match.group("hours")) != 1 or not named_action:
                return []
            # An expiry reference is never accepted without a matching printed Action.
            if not any(a.split(" (", 1)[0].casefold() == named_action.casefold()
                       for a in monster.action_names):
                return []
        action_ids = (
            [re.sub(r"\s+", "-", named_action.strip().casefold())]
            if named_action else []
        )
        return [TimedSelfBuffAction(
            id="invisibility", name="Invisibility", action_cost="action",
            condition_ids=["invisible"], magical_effect=True,
            concentration=True, ends_on_owner_attack=True,
            ends_on_owner_spell_cast=(rest_match is not None or
                (match is not None and match.group("spell") == " or casts a spell")),
            ends_on_owner_action_ids=action_ids, priority=70,
            resource_id="invisibility" if rest_match is not None else None,
            duration_rounds=600 if rest_match is not None else None,
            expiry_timing="source_turn_end" if rest_match is not None else None,
            animation="invisibility",
        )]
    except Exception:
        logger.exception("2014 source Invisibility binding failed for %s.", monster.id)
        raise


def source_invisibility_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    """A rest-recharge Action has one use during the standalone arena fight."""
    try:
        return [ResourceDefinition(id=action.resource_id, name=action.name, max_uses=1)
                for action in source_invisibility_action_2014(monster)
                if action.resource_id is not None]
    except Exception:
        logger.exception("Could not compile rest-charge Invisibility resource for %s.", monster.id)
        raise
