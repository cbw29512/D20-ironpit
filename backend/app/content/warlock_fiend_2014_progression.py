from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Warlock2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spells_known: int
    pact_slots: int
    pact_slot_level: int
    invocations_known: int
    mystic_arcanum_levels: tuple[int, ...]
    features_added: tuple[str, ...] = ()


_KNOWN=(2,3,4,5,6,7,8,9,10,10,11,11,12,12,13,13,14,14,15,15)
_SLOTS=(1,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,4,4,4,4)
_INV=(0,2,2,2,3,3,4,4,5,5,5,6,6,6,7,7,7,8,8,8)


def _arcanum(level: int) -> tuple[int, ...]:
    return tuple(spell_level for required, spell_level in ((11,6),(13,7),(15,8),(17,9)) if level >= required)


WARLOCK_FIEND_2014_LEVELS: dict[int, Warlock2014Level] = {}
for level in range(1, 21):
    pb=2+(level-1)//4
    cantrips=2 if level < 4 else 3 if level < 10 else 4
    slot_level=min(5, (level+1)//2)
    features={
        1:("pact-magic","dark-ones-blessing"),2:("eldritch-invocations",),3:("pact-boon",),
        4:("ability-score-improvement",),6:("dark-ones-own-luck",),8:("ability-score-improvement",),
        10:("fiendish-resilience",),11:("mystic-arcanum-6",),12:("ability-score-improvement",),
        13:("mystic-arcanum-7",),14:("hurl-through-hell",),15:("mystic-arcanum-8",),
        16:("ability-score-improvement",),17:("mystic-arcanum-9",),19:("ability-score-improvement",),
        20:("eldritch-master",),
    }.get(level, ())
    WARLOCK_FIEND_2014_LEVELS[level]=Warlock2014Level(
        level,pb,cantrips,_KNOWN[level-1],_SLOTS[level-1],slot_level,_INV[level-1],_arcanum(level),features,
    )


def warlock_fiend_2014_level(level: int) -> Warlock2014Level:
    try:
        return WARLOCK_FIEND_2014_LEVELS[level]
    except KeyError as exc:
        logger.exception("Invalid 2014 Fiend Warlock level %s.", level)
        raise ValueError("2014 Fiend Warlock level must be between 1 and 20.") from exc
