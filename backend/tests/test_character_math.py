import pytest

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.domain.character_builds import AbilityScores


def test_proficiency_bonus_follows_character_level_table() -> None:
    assert [proficiency_bonus(level) for level in (1, 4, 5, 9, 13, 17, 20)] == [2, 2, 3, 4, 5, 6, 6]
    with pytest.raises(ValueError):
        proficiency_bonus(0)


def test_fixed_hit_points_use_current_constitution_modifier_retroactively() -> None:
    assert fixed_hit_points(1, 10, 2) == 12
    assert fixed_hit_points(3, 10, 2) == 28
    assert fixed_hit_points(4, 10, 3) == 40
    assert fixed_hit_points(20, 10, 5) == 224


def test_saving_throw_bonuses_are_derived_from_scores_and_proficiencies() -> None:
    scores = AbilityScores(
        strength=17, dexterity=13, constitution=15,
        intelligence=10, wisdom=10, charisma=10,
    )
    saves = saving_throw_bonuses(scores, 1, ("strength", "constitution"))
    assert saves == {
        "strength": 5, "dexterity": 1, "constitution": 4,
        "intelligence": 0, "wisdom": 0, "charisma": 0,
    }
