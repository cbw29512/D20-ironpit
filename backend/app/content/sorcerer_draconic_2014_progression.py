from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Sorcerer2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spells_known: int
    sorcery_points: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()


def _s(*v: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*v, *([0] * (9 - len(v)))))  # type: ignore[return-value]


_KNOWN = (2,3,4,5,6,7,8,9,10,11,12,12,13,13,14,14,15,15,15,15)
_ROWS = {}
for level in range(1, 21):
    pb = 2 + (level - 1) // 4
    cantrips = 4 if level < 4 else 5 if level < 10 else 6
    slots_by_level = {
        1:(2,),2:(3,),3:(4,2),4:(4,3),5:(4,3,2),6:(4,3,3),7:(4,3,3,1),8:(4,3,3,2),
        9:(4,3,3,3,1),10:(4,3,3,3,2),11:(4,3,3,3,2,1),12:(4,3,3,3,2,1),
        13:(4,3,3,3,2,1,1),14:(4,3,3,3,2,1,1),15:(4,3,3,3,2,1,1,1),
        16:(4,3,3,3,2,1,1,1),17:(4,3,3,3,2,1,1,1,1),18:(4,3,3,3,3,1,1,1,1),
        19:(4,3,3,3,3,2,1,1,1),20:(4,3,3,3,3,2,2,1,1),
    }[level]
    features = {
        1:("spellcasting","draconic-resilience"),2:("font-of-magic",),3:("metamagic",),
        4:("ability-score-improvement",),6:("elemental-affinity",),8:("ability-score-improvement",),
        10:("metamagic-option",),12:("ability-score-improvement",),14:("dragon-wings",),
        16:("ability-score-improvement",),17:("metamagic-option",),18:("draconic-presence",),
        19:("ability-score-improvement",),20:("sorcerous-restoration",),
    }.get(level, ())
    _ROWS[level] = (pb, cantrips, _KNOWN[level - 1], max(0, level - 1), _s(*slots_by_level), features)


SORCERER_DRACONIC_2014_LEVELS = {
    level: Sorcerer2014Level(level, *row) for level, row in _ROWS.items()
}


def sorcerer_draconic_2014_level(level: int) -> Sorcerer2014Level:
    try:
        return SORCERER_DRACONIC_2014_LEVELS[level]
    except KeyError as exc:
        logger.exception("Invalid 2014 Draconic Sorcerer level %s.", level)
        raise ValueError("2014 Draconic Sorcerer level must be between 1 and 20.") from exc
