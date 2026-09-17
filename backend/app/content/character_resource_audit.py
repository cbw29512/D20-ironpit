from __future__ import annotations

from collections.abc import Callable

from app.content.level_resources import (
    barbarian_2014_rage_uses,
    barbarian_rage_uses,
    cleric_channel_divinity_uses,
    fighter_2014_action_surge_uses,
    fighter_2014_indomitable_uses,
    fighter_2014_second_wind_uses,
    fighter_action_surge_uses,
    fighter_indomitable_uses,
    fighter_second_wind_uses,
    orc_adrenaline_rush_uses,
)
from app.content.pregen_combat_profiles import PregenCombatProfile
from app.content.spell_slot_progression import FULL_CASTER_CLASSES, spell_slot_resources
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate

ResourceRule = tuple[str, str, Callable[[int], int]]

_2024_CLASS_RULES: dict[str, tuple[ResourceRule, ...]] = {
    "barbarian": (("rage", "Rage", barbarian_rage_uses),),
    "cleric": (("channel-divinity", "Channel Divinity", cleric_channel_divinity_uses),),
    "fighter": (
        ("second-wind", "Second Wind", fighter_second_wind_uses),
        ("action-surge", "Action Surge", fighter_action_surge_uses),
        ("indomitable", "Indomitable", fighter_indomitable_uses),
    ),
    "rogue": (),
}
_2014_CLASS_RULES: dict[str, tuple[ResourceRule, ...]] = {
    "barbarian": (("rage", "Rage", barbarian_2014_rage_uses),),
    "fighter": (
        ("second-wind", "Second Wind", fighter_2014_second_wind_uses),
        ("action-surge", "Action Surge", fighter_2014_action_surge_uses),
        ("indomitable", "Indomitable", fighter_2014_indomitable_uses),
    ),
}
_2024_SPECIES_RULES: dict[str, tuple[ResourceRule, ...]] = {
    "orc": (
        ("adrenaline-rush", "Adrenaline Rush", orc_adrenaline_rush_uses),
        ("relentless-endurance", "Relentless Endurance", lambda _level: 1),
    ),
}
_2014_SPECIES_RULES: dict[str, tuple[ResourceRule, ...]] = {
    "half-orc": (("relentless-endurance", "Relentless Endurance", lambda _level: 1),),
}


def _class_rules(profile: CharacterBuildProfile) -> dict[str, tuple[ResourceRule, ...]]:
    return _2014_CLASS_RULES if profile.ruleset == "2014" else _2024_CLASS_RULES


def expected_resources(profile: CharacterBuildProfile) -> dict[str, int]:
    """Return independently certified positive-use resources for this build's edition."""
    class_rules = _class_rules(profile)
    species_rules = _2014_SPECIES_RULES if profile.ruleset == "2014" else _2024_SPECIES_RULES
    rules = [
        *class_rules.get(profile.class_id, ()),
        *species_rules.get(profile.species_id, ()),
    ]
    resolved = {resource_id: resolver(profile.level) for resource_id, _name, resolver in rules}
    if profile.ruleset == "2024" and profile.class_id in FULL_CASTER_CLASSES:
        resolved.update(spell_slot_resources(profile.class_id, profile.level))
    return {resource_id: uses for resource_id, uses in resolved.items() if uses > 0}


def audit_character_resources(
    template: CombatantTemplate,
    build_profile: CharacterBuildProfile,
    combat_profile: PregenCombatProfile,
) -> list[str]:
    """Fail closed when runtime/profile resource counts disagree with edition-derived RAW rules."""
    issues: list[str] = []
    class_rules = _class_rules(build_profile)
    if build_profile.class_id not in class_rules:
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
