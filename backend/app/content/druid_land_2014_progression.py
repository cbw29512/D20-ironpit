from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Druid2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    wild_shape_uses: int
    wild_shape_unlimited: bool
    wild_shape_max_cr: str | None
    wild_shape_allows_swim: bool
    wild_shape_allows_fly: bool
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


DRUID_LAND_2014_LEVELS: dict[int, Druid2014Level] = {}
for level in range(1,21):
    pb=2+(level-1)//4
    cantrips=2 if level < 4 else 3 if level < 10 else 4
    if level < 2:
        uses=0; unlimited=False; max_cr=None; swim=False; fly=False
    else:
        uses=2
        unlimited=level == 20
        max_cr="1/4" if level < 4 else "1/2" if level < 8 else "1"
        swim=level >= 4; fly=level >= 8
    features={
        1:("spellcasting","druidic"),2:("wild-shape","land-bonus-cantrip","natural-recovery"),
        3:("land-circle-spells-2",),4:("wild-shape-improvement","ability-score-improvement"),
        5:("land-circle-spells-3",),6:("lands-stride",),7:("land-circle-spells-4",),
        8:("wild-shape-improvement","ability-score-improvement"),9:("land-circle-spells-5",),
        10:("natures-ward",),12:("ability-score-improvement",),14:("natures-sanctuary",),
        16:("ability-score-improvement",),18:("timeless-body","beast-spells"),
        19:("ability-score-improvement",),20:("archdruid",),
    }.get(level, ())
    DRUID_LAND_2014_LEVELS[level]=Druid2014Level(
        level,pb,cantrips,uses,unlimited,max_cr,swim,fly,_s(*_SLOTS[level]),features,
    )


def druid_land_2014_level(level: int) -> Druid2014Level:
    try:
        return DRUID_LAND_2014_LEVELS[level]
    except KeyError as exc:
        logger.exception("Invalid 2014 Land Druid level %s.", level)
        raise ValueError("2014 Land Druid level must be between 1 and 20.") from exc
