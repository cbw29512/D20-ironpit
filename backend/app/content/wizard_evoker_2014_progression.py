from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Wizard2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spellbook_minimum: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()


def _s(*v: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*v, *([0] * (9 - len(v)))))  # type: ignore[return-value]


_SLOTS={
1:(2,),2:(3,),3:(4,2),4:(4,3),5:(4,3,2),6:(4,3,3),7:(4,3,3,1),8:(4,3,3,2),
9:(4,3,3,3,1),10:(4,3,3,3,2),11:(4,3,3,3,2,1),12:(4,3,3,3,2,1),
13:(4,3,3,3,2,1,1),14:(4,3,3,3,2,1,1),15:(4,3,3,3,2,1,1,1),
16:(4,3,3,3,2,1,1,1),17:(4,3,3,3,2,1,1,1,1),18:(4,3,3,3,3,1,1,1,1),
19:(4,3,3,3,3,2,1,1,1),20:(4,3,3,3,3,2,2,1,1),
}


WIZARD_EVOKER_2014_LEVELS: dict[int, Wizard2014Level] = {}
for level in range(1,21):
    pb=2+(level-1)//4
    cantrips=3 if level < 4 else 4 if level < 10 else 5
    features={
        1:("spellcasting","arcane-recovery"),2:("evocation-savant","sculpt-spells"),
        4:("ability-score-improvement",),6:("potent-cantrip",),8:("ability-score-improvement",),
        10:("empowered-evocation",),12:("ability-score-improvement",),14:("overchannel",),
        16:("ability-score-improvement",),18:("spell-mastery",),19:("ability-score-improvement",),
        20:("signature-spells",),
    }.get(level, ())
    WIZARD_EVOKER_2014_LEVELS[level]=Wizard2014Level(
        level,pb,cantrips,6 + 2 * (level - 1),_s(*_SLOTS[level]),features,
    )


def wizard_evoker_2014_level(level: int) -> Wizard2014Level:
    try:
        return WIZARD_EVOKER_2014_LEVELS[level]
    except KeyError as exc:
        logger.exception("Invalid 2014 Evoker Wizard level %s.", level)
        raise ValueError("2014 Evoker Wizard level must be between 1 and 20.") from exc
