from __future__ import annotations

from app.content.character_resource_rules import (
    class_resource_rules,
    expected_resources,
    expected_unlimited_resources,
)
from app.content.pregen_combat_profiles import PregenCombatProfile
from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate


def audit_character_resources(
    template: CombatantTemplate,
    build_profile: CharacterBuildProfile,
    combat_profile: PregenCombatProfile,
) -> list[str]:
    """Fail closed when runtime/profile resource counts disagree with edition-derived RAW rules."""
    issues: list[str] = []
    class_rules = class_resource_rules(build_profile)
    if build_profile.class_id not in class_rules:
        issues.append("class-level-resource-rules-not-certified")
    expected = expected_resources(build_profile)
    runtime = {item.id: item.max_uses for item in template.resources}
    fingerprint = dict(combat_profile.resources)
    if runtime != expected:
        issues.append("level-derived-runtime-resources-mismatch")
    if fingerprint != expected:
        issues.append("level-derived-combat-profile-resources-mismatch")
    expected_unlimited = expected_unlimited_resources(build_profile)
    if tuple(template.unlimited_resource_ids) != expected_unlimited:
        issues.append("level-derived-runtime-unlimited-resources-mismatch")
    if tuple(combat_profile.unlimited_resources) != expected_unlimited:
        issues.append("level-derived-combat-profile-unlimited-resources-mismatch")
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
