from __future__ import annotations

from collections.abc import Callable

from app.content.level_resources import (
    barbarian_rage_uses,
    fighter_second_wind_uses,
    orc_adrenaline_rush_uses,
)
from app.content.pregen_combat_profiles import PregenCombatProfile
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate

ResourceRule = tuple[str, str, Callable[[int], int]]

# A class must appear here, even with an empty tuple, before its level-scaling
# resource rules are considered independently audited for RAW certification.
_CLASS_RULES: dict[str, tuple[ResourceRule, ...]] = {
    "barbarian": (("rage", "Rage", barbarian_rage_uses),),
    "fighter": (("second-wind", "Second Wind", fighter_second_wind_uses),),
}
_SPECIES_RULES: dict[str, tuple[ResourceRule, ...]] = {
    "orc": (
        ("adrenaline-rush", "Adrenaline Rush", orc_adrenaline_rush_uses),
        ("relentless-endurance", "Relentless Endurance", lambda _level: 1),
    ),
}


def expected_resources(profile: CharacterBuildProfile) -> dict[str, int]:
    """Return every independently certified limited-use resource for this build."""
    rules = [
        *_CLASS_RULES.get(profile.class_id, ()),
        *_SPECIES_RULES.get(profile.species_id, ()),
    ]
    return {resource_id: resolver(profile.level) for resource_id, _name, resolver in rules}


def audit_character_resources(
    template: CombatantTemplate,
    build_profile: CharacterBuildProfile,
    combat_profile: PregenCombatProfile,
) -> list[str]:
    """Fail closed when runtime/profile resource counts disagree with level-derived RAW rules."""
    issues: list[str] = []
    if build_profile.class_id not in _CLASS_RULES:
        issues.append("class-level-resource-rules-not-certified")
    expected = expected_resources(build_profile)
    runtime = {item.id: item.max_uses for item in template.resources}
    fingerprint = dict(combat_profile.resources)
    if runtime != expected:
        issues.append("level-derived-runtime-resources-mismatch")
    if fingerprint != expected:
        issues.append("level-derived-combat-profile-resources-mismatch")
    return issues


def assert_character_resources_raw_ready(
    template: CombatantTemplate,
    build_profile: CharacterBuildProfile,
    combat_profile: PregenCombatProfile,
) -> None:
    issues = audit_character_resources(template, build_profile, combat_profile)
    if issues:
        raise ValueError(
            f"Pregen resource audit failed for {template.id}: " + ", ".join(issues)
        )
