from dataclasses import replace

from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.character_resource_audit import audit_character_resources
from app.content.audited_rogue import build_mara_quickstep_level
from app.content.rogue_final_progression_profile import build_mara_quickstep_level20_profile
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


def test_class_without_independent_level_resource_rules_fails_closed() -> None:
    template = build_rokhan_stonefury().model_copy(deep=True)
    build_profile = build_rokhan_stonefury_profile().model_copy(
        update={"class_id": "bard", "class_name": "Bard"}
    )
    combat_profile = build_pregen_combat_profiles()[template.id]

    assert "class-level-resource-rules-not-certified" in audit_character_resources(
        template, build_profile, combat_profile
    )



def test_2024_rogue_level20_stroke_of_luck_resource_matches_independent_audit() -> None:
    template = build_mara_quickstep_level(20)
    build_profile = build_mara_quickstep_level20_profile()
    combat_profile = build_pregen_combat_profiles()[template.id]

    assert {item.id: item.max_uses for item in template.resources}["stroke-of-luck"] == 1
    assert dict(combat_profile.resources)["stroke-of-luck"] == 1
    assert audit_character_resources(template, build_profile, combat_profile) == []
