from __future__ import annotations

import logging

from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)

BASE_SCORES = AbilityScores(
    strength=12, dexterity=15, constitution=13,
    intelligence=10, wisdom=14, charisma=8,
)
HUMAN_INCREASES = {
    "strength": 1, "dexterity": 1, "constitution": 1,
    "intelligence": 1, "wisdom": 1, "charisma": 1,
}
ASI_CHOICES: tuple[tuple[int, str, int], ...] = (
    (4, "dexterity", 2),
    (8, "dexterity", 2),
    (12, "wisdom", 2),
    (16, "wisdom", 2),
    (19, "wisdom", 1),
    (19, "constitution", 1),
)


def ability_scores(level: int) -> AbilityScores:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Hunter Ranger level must be between 1 and 20.")
        values = BASE_SCORES.model_dump()
        for ability, amount in HUMAN_INCREASES.items():
            values[ability] += amount
        for required, ability, amount in ASI_CHOICES:
            if level >= required:
                values[ability] += amount
        return AbilityScores(**values)
    except Exception:
        logger.exception("Failed to resolve Rowan's 2014 ability scores at level %s.", level)
        raise
