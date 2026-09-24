from __future__ import annotations

import logging

from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)

# 2014 Lyra is a Half-Elf College of Lore Bard. This is immutable build/source data.
BASE_SCORES = AbilityScores(
    strength=8,
    dexterity=14,
    constitution=13,
    intelligence=10,
    wisdom=12,
    charisma=15,
)

HALF_ELF_INCREASES = {
    "charisma": 2,
    "dexterity": 1,
    "constitution": 1,
}

ASI_CHOICES: tuple[tuple[int, str, int], ...] = (
    (4, "charisma", 2),
    (8, "charisma", 1),
    (8, "dexterity", 1),
    (12, "dexterity", 2),
    (16, "constitution", 2),
    (19, "dexterity", 2),
)

SPELL_SLOTS: dict[int, tuple[int, ...]] = {
    1: (2,), 2: (3,), 3: (4, 2), 4: (4, 3),
    5: (4, 3, 2), 6: (4, 3, 3), 7: (4, 3, 3, 1), 8: (4, 3, 3, 2),
    9: (4, 3, 3, 3, 1), 10: (4, 3, 3, 3, 2), 11: (4, 3, 3, 3, 2, 1),
    12: (4, 3, 3, 3, 2, 1), 13: (4, 3, 3, 3, 2, 1, 1),
    14: (4, 3, 3, 3, 2, 1, 1), 15: (4, 3, 3, 3, 2, 1, 1, 1),
    16: (4, 3, 3, 3, 2, 1, 1, 1), 17: (4, 3, 3, 3, 2, 1, 1, 1, 1),
    18: (4, 3, 3, 3, 3, 1, 1, 1, 1), 19: (4, 3, 3, 3, 3, 2, 1, 1, 1),
    20: (4, 3, 3, 3, 3, 2, 2, 1, 1),
}

SPELLS_KNOWN = (
    4, 5, 6, 7, 8, 9, 10, 11, 12, 14,
    15, 15, 16, 18, 19, 19, 20, 22, 22, 22,
)

CANTRIPS_KNOWN = (
    2, 2, 2, 3, 3, 3, 3, 3, 3, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
)

FEATURE_LEVELS = {
    "bardic-inspiration": 1,
    "jack-of-all-trades": 2,
    "song-of-rest": 2,
    "college-lore": 3,
    "expertise": 3,
    "cutting-words": 3,
    "font-of-inspiration": 5,
    "countercharm": 6,
    "additional-magical-secrets": 6,
    "magical-secrets": 10,
    "peerless-skill": 14,
    "superior-inspiration": 20,
}


def ability_scores(level: int) -> AbilityScores:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lore Bard level must be between 1 and 20.")
        values = BASE_SCORES.model_dump()
        for ability, amount in HALF_ELF_INCREASES.items():
            values[ability] += amount
        for required, ability, amount in ASI_CHOICES:
            if level >= required:
                values[ability] += amount
        return AbilityScores(**values)
    except Exception:
        logger.exception("Failed to resolve 2014 Lyra ability scores at level %s", level)
        raise


def bardic_inspiration_die(level: int) -> int:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lore Bard level must be between 1 and 20.")
        if level >= 15:
            return 12
        if level >= 10:
            return 10
        if level >= 5:
            return 8
        return 6
    except Exception:
        logger.exception("Failed to resolve 2014 Bardic Inspiration die at level %s", level)
        raise
