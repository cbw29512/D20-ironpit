from __future__ import annotations

from app.domain.character_builds import AbilityName, AbilityScores

ALL_ABILITIES: tuple[AbilityName, ...] = (
    "strength", "dexterity", "constitution",
    "intelligence", "wisdom", "charisma",
)


def proficiency_bonus(level: int) -> int:
    if not 1 <= level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    return 2 + (level - 1) // 4


def fixed_hit_points(level: int, hit_die_size: int, constitution_modifier: int) -> int:
    if not 1 <= level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    if hit_die_size < 4 or hit_die_size % 2:
        raise ValueError("Hit Die size must be an even die of at least d4.")
    fixed_gain = hit_die_size // 2 + 1
    return hit_die_size + constitution_modifier + (level - 1) * (fixed_gain + constitution_modifier)


def saving_throw_bonuses(
    scores: AbilityScores,
    level: int,
    proficient_abilities: tuple[AbilityName, ...],
) -> dict[str, int]:
    pb = proficiency_bonus(level)
    proficient = set(proficient_abilities)
    return {
        ability: scores.modifier(ability) + (pb if ability in proficient else 0)
        for ability in ALL_ABILITIES
    }


def skill_bonus(
    scores: AbilityScores,
    level: int,
    ability: AbilityName,
    *,
    proficient: bool,
) -> int:
    return scores.modifier(ability) + (proficiency_bonus(level) if proficient else 0)
