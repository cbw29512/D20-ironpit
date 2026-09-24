from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Bard2014Level:
    level: int
    proficiency_bonus: int
    cantrips_known: int
    spells_known: int
    bardic_die_size: int
    spell_slots: tuple[int, int, int, int, int, int, int, int, int]
    features_added: tuple[str, ...] = ()


def _s(*v: int) -> tuple[int, int, int, int, int, int, int, int, int]:
    return tuple((*v, *([0] * (9 - len(v)))))  # type: ignore[return-value]


_ROWS = {
    1:(2,2,4,6,_s(2),("spellcasting","bardic-inspiration")),
    2:(2,2,5,6,_s(3),("jack-of-all-trades","song-of-rest-d6")),
    3:(2,2,6,6,_s(4,2),("expertise","lore-cutting-words")),
    4:(2,3,7,6,_s(4,3),("ability-score-improvement",)),
    5:(3,3,8,8,_s(4,3,2),("font-of-inspiration",)),
    6:(3,3,9,8,_s(4,3,3),("countercharm","lore-additional-magical-secrets")),
    7:(3,3,10,8,_s(4,3,3,1),()), 8:(3,3,11,8,_s(4,3,3,2),("ability-score-improvement",)),
    9:(4,3,12,8,_s(4,3,3,3,1),("song-of-rest-d8",)),
    10:(4,4,14,10,_s(4,3,3,3,2),("expertise","magical-secrets")),
    11:(4,4,15,10,_s(4,3,3,3,2,1),()), 12:(4,4,15,10,_s(4,3,3,3,2,1),("ability-score-improvement",)),
    13:(5,4,16,10,_s(4,3,3,3,2,1,1),("song-of-rest-d10",)),
    14:(5,4,18,10,_s(4,3,3,3,2,1,1),("magical-secrets","lore-peerless-skill")),
    15:(5,4,19,12,_s(4,3,3,3,2,1,1,1),()), 16:(5,4,19,12,_s(4,3,3,3,2,1,1,1),("ability-score-improvement",)),
    17:(6,4,20,12,_s(4,3,3,3,2,1,1,1,1),("song-of-rest-d12",)),
    18:(6,4,22,12,_s(4,3,3,3,3,1,1,1,1),("magical-secrets",)),
    19:(6,4,22,12,_s(4,3,3,3,3,2,1,1,1),("ability-score-improvement",)),
    20:(6,4,22,12,_s(4,3,3,3,3,2,2,1,1),("superior-inspiration",)),
}


BARD_LORE_2014_LEVELS = {
    level: Bard2014Level(level, pb, cantrips, known, die, slots, features)
    for level, (pb, cantrips, known, die, slots, features) in _ROWS.items()
}


def bard_lore_2014_level(level: int) -> Bard2014Level:
    try:
        return BARD_LORE_2014_LEVELS[level]
    except KeyError as exc:
        logger.exception("Invalid 2014 Lore Bard level %s.", level)
        raise ValueError("2014 Lore Bard level must be between 1 and 20.") from exc
