from __future__ import annotations

from app.content.canonical_hero_policy import (
    assert_canonical_identity,
    assert_canonical_profile_policy,
    canonical_template_id,
)
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate


def advance_template_data(
    previous: CombatantTemplate,
    class_id: str,
    next_level: int,
) -> dict[str, object]:
    """Clone the previous canonical level and advance identity exactly one level."""
    if previous.level is None or next_level != previous.level + 1:
        raise ValueError("Canonical runtime progression must advance exactly one level at a time.")
    hero = HERO_BY_CLASS[class_id]
    assert_canonical_identity(class_id, previous.name, previous.level)
    if previous.id != canonical_template_id(class_id, previous.level):
        raise ValueError("Previous canonical runtime template identity drifted.")
    data = previous.model_dump()
    data.update(
        id=canonical_template_id(class_id, next_level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=next_level,
    )
    return data


def advance_profile_data(
    previous: CharacterBuildProfile,
    next_level: int,
) -> dict[str, object]:
    """Clone the previous canonical build profile and advance exactly one level."""
    assert_canonical_profile_policy(previous)
    if next_level != previous.level + 1:
        raise ValueError("Canonical build progression must advance exactly one level at a time.")
    slug = previous.character_name.lower().replace(" ", "-")
    data = previous.model_dump()
    data.update(
        id=f"build-{slug}-l{next_level}",
        template_id=canonical_template_id(previous.class_id, next_level),
        level=next_level,
    )
    return data
