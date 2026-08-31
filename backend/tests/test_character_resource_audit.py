from dataclasses import replace

from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.character_resource_audit import audit_character_resources
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.models import ResourceDefinition


def test_level_resource_audit_rejects_matching_wrong_runtime_and_profile_counts() -> None:
    template = build_rokhan_stonefury().model_copy(deep=True)
    build_profile = build_rokhan_stonefury_profile()
    combat_profile = build_pregen_combat_profiles()[template.id]

    template.resources = [
        ResourceDefinition(id="rage", name="Rage", max_uses=99),
        ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=2),
        ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
    ]
    bad_profile = replace(
        combat_profile,
        resources=(("rage", 99), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
    )

    issues = audit_character_resources(template, build_profile, bad_profile)
    assert "level-derived-runtime-resources-mismatch" in issues
    assert "level-derived-combat-profile-resources-mismatch" in issues


def test_unknown_limited_runtime_resource_fails_closed() -> None:
    template = build_rokhan_stonefury().model_copy(deep=True)
    build_profile = build_rokhan_stonefury_profile()
    combat_profile = build_pregen_combat_profiles()[template.id]
    template.resources.append(ResourceDefinition(id="mystery-power", name="Mystery Power", max_uses=1))

    assert "level-derived-runtime-resources-mismatch" in audit_character_resources(
        template, build_profile, combat_profile
    )
