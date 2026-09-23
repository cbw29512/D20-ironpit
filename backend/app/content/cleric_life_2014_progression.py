from __future__ import annotations

from app.domain.character_builds import AbilityIncrease, AbilityScores


def base_scores_2014() -> AbilityScores:
    return AbilityScores(
        strength=13, dexterity=10, constitution=14,
        intelligence=8, wisdom=15, charisma=12,
    )


def species_increases_2014() -> list[AbilityIncrease]:
    return [
        AbilityIncrease(ability="constitution", amount=2),
        AbilityIncrease(ability="wisdom", amount=1),
    ]


def advancement_increases_2014(level: int) -> list[AbilityIncrease]:
    milestones = (
        (4, "wisdom", 2),
        (8, "wisdom", 2),
        (12, "constitution", 2),
        (16, "constitution", 2),
        (19, "strength", 2),
    )
    return [
        AbilityIncrease(ability=ability, amount=amount)
        for required_level, ability, amount in milestones
        if level >= required_level
    ]


def final_scores_2014(level: int) -> AbilityScores:
    base = base_scores_2014()
    values = base.model_dump()
    for increase in [*species_increases_2014(), *advancement_increases_2014(level)]:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)
