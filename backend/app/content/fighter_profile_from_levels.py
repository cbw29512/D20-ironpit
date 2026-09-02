from __future__ import annotations

from app.content.fighter_combat_levels import FIGHTER_COMBAT_LEVELS
from app.domain.character_builds import AbilityIncrease, AbilityScores


_ADVANCEMENT_INCREASES = {
    4: (("strength", 1), ("constitution", 1)),
    6: (("strength", 2),),
    8: (("constitution", 2),),
    12: (("constitution", 2),),
    14: (("dexterity", 2),),
    16: (("dexterity", 2),),
    19: (("dexterity", 1),),
}


def fighter_advancement_increases(level: int) -> list[AbilityIncrease]:
    if level not in FIGHTER_COMBAT_LEVELS:
        raise ValueError(f"Fighter level {level} must be between 1 and 20.")
    increases: list[AbilityIncrease] = []
    for current in range(1, level + 1):
        increases.extend(AbilityIncrease(ability=ability, amount=amount)
                         for ability, amount in _ADVANCEMENT_INCREASES.get(current, ()))
    return increases


def apply_fighter_level_to_profile_data(data: dict[str, object], level: int) -> None:
    row = FIGHTER_COMBAT_LEVELS[level]
    data.update(
        advancement_increases=[item.model_dump() for item in fighter_advancement_increases(level)],
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
