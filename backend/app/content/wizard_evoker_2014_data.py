from __future__ import annotations

import logging

from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)

BASE_SCORES = AbilityScores(
    strength=8, dexterity=14, constitution=13,
    intelligence=15, wisdom=12, charisma=10,
)
HUMAN_INCREASES = {
    "strength": 1, "dexterity": 1, "constitution": 1,
    "intelligence": 1, "wisdom": 1, "charisma": 1,
}
ASI_CHOICES: tuple[tuple[int, str, int], ...] = (
    (4, "intelligence", 2),
    (8, "intelligence", 2),
    (12, "constitution", 2),
    (16, "dexterity", 1),
    (16, "constitution", 1),
    (19, "dexterity", 1),
    (19, "constitution", 1),
)


def ability_scores(level: int) -> AbilityScores:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Evoker Wizard level must be between 1 and 20.")
        values = BASE_SCORES.model_dump()
        for ability, amount in HUMAN_INCREASES.items():
            values[ability] += amount
        for required, ability, amount in ASI_CHOICES:
            if level >= required:
                values[ability] += amount
        return AbilityScores(**values)
    except Exception:
        logger.exception("Failed to resolve Elian's 2014 ability scores at level %s.", level)
        raise
