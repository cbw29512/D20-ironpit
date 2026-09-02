from __future__ import annotations

from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.domain.character_builds import AbilityIncrease, AbilityScores


_ADVANCEMENT_INCREASES = {
    4: (("wisdom", 2),),
    8: (("wisdom", 1), ("charisma", 1)),
    12: (("charisma", 2),),
    16: (("charisma", 2),),
    19: (("charisma", 1),),
}


def cleric_advancement_increases(level: int) -> list[AbilityIncrease]:
    if level not in CLERIC_COMBAT_LEVELS:
        raise ValueError(f"Cleric level {level} must be between 1 and 20.")
    increases: list[AbilityIncrease] = []
    for current in range(1, level + 1):
        increases.extend(AbilityIncrease(ability=ability, amount=amount)
                         for ability, amount in _ADVANCEMENT_INCREASES.get(current, ()))
    return increases


def apply_cleric_level_to_profile_data(data: dict[str, object], level: int) -> None:
    row = CLERIC_COMBAT_LEVELS[level]
    data.update(
        advancement_increases=[item.model_dump() for item in cleric_advancement_increases(level)],
        final_ability_scores=AbilityScores(
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=14,
            wisdom=row.wisdom,
            charisma=row.charisma,
        ).model_dump(),
    )
