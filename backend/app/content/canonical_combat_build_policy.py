from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.domain.character_builds import AbilityIncrease, AbilityName, AbilityScores

CombatBuildRole = Literal["melee", "ranged", "caster"]


@dataclass(frozen=True)
class CanonicalStatPriority:
    role: CombatBuildRole
    primary: AbilityName
    secondary: AbilityName
    tertiary: AbilityName


CANONICAL_POINT_BUY_ARRAY = (15, 14, 13, 10, 10, 10)

CANONICAL_STAT_PRIORITIES: dict[str, CanonicalStatPriority] = {
    "barbarian": CanonicalStatPriority("melee", "strength", "constitution", "dexterity"),
    "bard": CanonicalStatPriority("caster", "charisma", "wisdom", "intelligence"),
    "cleric": CanonicalStatPriority("caster", "wisdom", "charisma", "intelligence"),
    "druid": CanonicalStatPriority("caster", "wisdom", "charisma", "intelligence"),
    "fighter": CanonicalStatPriority("melee", "strength", "constitution", "dexterity"),
    "monk": CanonicalStatPriority("melee", "dexterity", "constitution", "strength"),
    "paladin": CanonicalStatPriority("melee", "strength", "constitution", "dexterity"),
    "ranger": CanonicalStatPriority("ranged", "dexterity", "constitution", "strength"),
    "rogue": CanonicalStatPriority("ranged", "dexterity", "constitution", "strength"),
    "sorcerer": CanonicalStatPriority("caster", "charisma", "wisdom", "intelligence"),
    "warlock": CanonicalStatPriority("caster", "charisma", "wisdom", "intelligence"),
    "wizard": CanonicalStatPriority("caster", "intelligence", "wisdom", "charisma"),
}


ABILITY_NAMES: tuple[AbilityName, ...] = (
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
)


def canonical_stat_priority(class_id: str) -> CanonicalStatPriority:
    priority = CANONICAL_STAT_PRIORITIES.get(class_id)
    if priority is None:
        raise ValueError(f"Unknown canonical class stat policy: {class_id}.")
    return priority


def canonical_base_ability_scores(class_id: str) -> AbilityScores:
    priority = canonical_stat_priority(class_id)
    values: dict[AbilityName, int] = {ability: 10 for ability in ABILITY_NAMES}
    values[priority.primary] = 15
    values[priority.secondary] = 14
    values[priority.tertiary] = 13
    return AbilityScores(**values)


def canonical_background_increases(
    class_id: str,
    allowed_abilities: list[AbilityName],
) -> list[AbilityIncrease]:
    """Choose deterministic legal +2/+1 increases without inflating a dump score."""
    priority = canonical_stat_priority(class_id)
    allowed = set(allowed_abilities)
    if priority.primary not in allowed:
        raise ValueError(
            f"{class_id} canonical Background must allow its primary {priority.primary} ability."
        )
    secondary = next(
        (ability for ability in (priority.secondary, priority.tertiary) if ability in allowed),
        None,
    )
    if secondary is None:
        raise ValueError(
            f"{class_id} canonical Background must allow a second non-dump priority ability."
        )
    return [
        AbilityIncrease(ability=priority.primary, amount=2),
        AbilityIncrease(ability=secondary, amount=1),
    ]


def assert_canonical_base_array(class_id: str, scores: AbilityScores) -> None:
    expected = canonical_base_ability_scores(class_id)
    if scores != expected:
        raise ValueError(
            f"{class_id} canonical base abilities drifted: "
            f"{scores.model_dump()} != {expected.model_dump()}."
        )
