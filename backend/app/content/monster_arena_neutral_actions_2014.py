"""Source proofs for 2014 Actions approved as arena-neutral.

These are source admission checks, never runtime ability-name dispatch.
Equipment corrosion remains inactive in the Pit; the printed Action is retained
on the card but does not change combat state.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

# Approved 2026-10-24: Antennae is arena-neutral. No equipment-penalty
# primitive is added because the effect is unique to this creature and the
# Pit does not track permanent armor or weapon damage penalties.
_APPROVED_NEUTRAL_ACTION_CLAUSES = {
    "Antennae": (
        "The rust monster corrodes a nonmagical ferrous metal object it can see "
        "within 5 feet of it. If the object isn't being worn or carried, the "
        "touch destroys a 1-foot cube of it. If the object is being worn or "
        "carried by a creature, the creature can make a DC 11 Dexterity saving "
        "throw to avoid the rust monster's touch. If the object touched is "
        "either metal armor or a metal shield being worn or carried, it takes a "
        "permanent and cumulative \u22121 penalty to the AC it offers. Armor reduced "
        "to an AC of 10 or a shield that drops to a +0 bonus is destroyed. If "
        "the object touched is a held metal weapon, it rusts as described in "
        "the Rust Metal trait."
    ),
}


def verified_arena_neutral_action_2014(monster: SourceMonster2014, action_name: str) -> bool:
    """Accept only the complete printed clause of an approved neutral Action."""
    try:
        if action_name not in monster.action_names:
            return False
        expected = _APPROVED_NEUTRAL_ACTION_CLAUSES.get(action_name)
        if expected is None:
            return False
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(action_name)
        if printed is None:
            return False
        return " ".join(printed.casefold().split()) == " ".join(expected.casefold().split())
    except Exception:
        logger.exception(
            "Approved neutral action proof failed for %s/%s.",
            monster.id, action_name,
        )
        raise
