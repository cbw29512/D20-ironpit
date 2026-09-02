from __future__ import annotations

from app.content.barbarian_combat_levels import BARBARIAN_COMBAT_LEVELS
from app.domain.character_builds import AbilityIncrease, AbilityScores


_ADVANCEMENT_INCREASES = {
    4: (("strength", 1), ("constitution", 1)),
    8: (("strength", 2),),
    12: (("constitution", 2),),
    16: (("constitution", 2),),
    19: (("strength", 1),),
}


def barbarian_advancement_increases(level: int) -> list[AbilityIncrease]:
    if level not in BARBARIAN_COMBAT_LEVELS:
        raise ValueError(f"Barbarian level {level} must be between 1 and 20.")
    increases: list[AbilityIncrease] = []
    for current in range(1, level + 1):
        increases.extend(AbilityIncrease(ability=ability, amount=amount)
                         for ability, amount in _ADVANCEMENT_INCREASES.get(current, ()))
    return increases


def apply_barbarian_level_to_profile_data(data: dict[str, object], level: int) -> None:
    row = BARBARIAN_COMBAT_LEVELS[level]
    data.update(
        advancement_increases=[item.model_dump() for item in barbarian_advancement_increases(level)],
        final_ability_scores=AbilityScores(
            strength=row.strength,
            dexterity=row.dexterity,
            constitution=row.constitution,
            intelligence=10,
            wisdom=10,
            charisma=10,
        ).model_dump(),
        weapon_masteries=list(row.weapon_masteries),
    )
