import pytest

from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.pregens import build_brom_ironmark
from app.domain.character_builds import (
    AbilityIncrease,
    AbilityScores,
    CharacterBuildProfile,
    FeatureAudit,
)


def _audit(feature_id: str, category: str, *, automated: bool = True) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_id.replace("-", " ").title(),
        source_reference="2024 Basic Rules",
        category=category,
        combat_relevant=True,
        automated=automated,
    )


def _profile() -> CharacterBuildProfile:
    template = build_brom_ironmark()
    return CharacterBuildProfile(
        id="audit-test-fighter",
        template_id=template.id,
        character_name=template.name,
        class_id="fighter",
        class_name="Fighter",
        level=1,
        species_id="gnome",
        species_name="Gnome",
        background_id="soldier",
        background_name="Soldier",
        origin_feat_id="savage-attacker",
        origin_feat_name="Savage Attacker",
        base_ability_scores=AbilityScores(str=15, dex=13, con=14, int=10, wis=12, cha=8),
        background_allowed_abilities=["str", "dex", "con"],
        background_increases=[
            AbilityIncrease(ability="str", amount=2),
            AbilityIncrease(ability="con", amount=1),
        ],
        final_ability_scores=AbilityScores(str=17, dex=13, con=15, int=10, wis=12, cha=8),
        class_equipment_option="gold",
        class_equipment=["Chain Mail", "Greataxe", "Dungeoneer's Pack"],
        background_equipment_option="package",
        background_equipment=["Spear", "Shortbow", "20 Arrows", "Traveler's Clothes"],
        skill_proficiencies=["Athletics", "Intimidation"],
        weapon_masteries=template.weapon_masteries,
        fighting_style=template.fighting_style,
        feature_audits=[
            _audit("fighting-style", "class"),
            _audit("gnomish-cunning", "species"),
            _audit("savage-attacker", "feat"),
            _audit("chain-mail", "equipment"),
        ],
        source_references=["2024 Basic Rules: Fighter", "2024 Basic Rules: Character Origins"],
    )


def test_complete_profile_passes_structural_raw_audit() -> None:
    template = build_brom_ironmark()
    profile = _profile()

    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    assert profile.final_ability_scores.modifier("str") == 3


def test_background_increases_must_follow_2024_pattern_and_allowed_scores() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.background_increases = [
        AbilityIncrease(ability="str", amount=1),
        AbilityIncrease(ability="wis", amount=2),
    ]

    issues = audit_character_build(profile, template)

    assert "background-increase-uses-disallowed-ability" in issues
    assert "final-str-does-not-match-background-increases" in issues
    assert "final-con-does-not-match-background-increases" in issues


def test_any_unautomated_combat_feature_blocks_raw_ready_claim() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.feature_audits[2].automated = False

    issues = audit_character_build(profile, template)

    assert "combat-feature-not-automated:savage-attacker" in issues
    with pytest.raises(ValueError, match="savage-attacker"):
        assert_character_build_raw_ready(profile, template)


def test_runtime_template_identity_and_build_choices_must_match_profile() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.template_id = "wrong-template"
    profile.level = 2
    profile.weapon_masteries = ["dagger"]
    profile.fighting_style = "Archery"

    issues = audit_character_build(profile, template)

    assert "runtime-template-id-mismatch" in issues
    assert "runtime-level-mismatch" in issues
    assert "runtime-weapon-masteries-mismatch" in issues
    assert "runtime-fighting-style-mismatch" in issues


def test_feature_audit_requires_class_species_feat_and_equipment_coverage() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.feature_audits = [_audit("fighting-style", "class")]

    issues = audit_character_build(profile, template)

    assert "missing-species-feature-audit" in issues
    assert "missing-feat-feature-audit" in issues
    assert "missing-equipment-feature-audit" in issues
    assert "origin-feat-missing-from-feature-audit" in issues
