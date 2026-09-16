import pytest
from pydantic import ValidationError

from app.content.build_audit import audit_character_build
from app.content.pregens import build_brom_ironmark
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


def _scores(strength: int, constitution: int) -> AbilityScores:
    return AbilityScores(
        strength=strength,
        dexterity=13,
        constitution=constitution,
        intelligence=10,
        wisdom=12,
        charisma=8,
    )


def _feature(feature_id: str, category: str) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_id.replace("-", " ").title(),
        source_reference="Basic Rules 2014",
        category=category,
        combat_relevant=True,
        automated=True,
    )


def _profile_2014() -> CharacterBuildProfile:
    template = build_brom_ironmark()
    return CharacterBuildProfile(
        id="audit-test-fighter-2014",
        template_id=template.id,
        character_name=template.name,
        class_id="fighter",
        class_name="Fighter",
        level=1,
        ruleset="2014",
        species_id="half-orc",
        species_name="Half-Orc",
        background_id="soldier",
        background_name="Soldier",
        base_ability_scores=_scores(15, 14),
        species_increases=[
            AbilityIncrease(ability="strength", amount=2),
            AbilityIncrease(ability="constitution", amount=1),
        ],
        final_ability_scores=_scores(17, 15),
        class_equipment_option="package",
        class_equipment=["Chain Mail", "Greatsword", "Light Crossbow", "20 Bolts"],
        background_equipment_option="package",
        background_equipment=["Insignia of Rank", "Common Clothes"],
        skill_proficiencies=["Athletics", "Intimidation"],
        fighting_style=template.fighting_style,
        feature_audits=[
            _feature("fighting-style-defense", "class"),
            _feature("relentless-endurance", "species"),
            _feature("greatsword", "equipment"),
        ],
        source_references=["Basic Rules 2014: Fighter", "Basic Rules 2014: Half-Orc"],
    )


def test_2014_profile_uses_species_asi_without_origin_feat_or_mastery() -> None:
    profile = _profile_2014()

    assert profile.ruleset == "2014"
    assert profile.origin_feat_id is None
    assert profile.background_increases == []
    assert profile.species_increases[0].ability == "strength"
    assert profile.weapon_masteries == []


def test_2014_profile_rejects_2024_weapon_mastery() -> None:
    data = _profile_2014().model_dump()
    data["weapon_masteries"] = ["greatsword"]

    with pytest.raises(ValidationError, match="Weapon Mastery"):
        CharacterBuildProfile.model_validate(data)


def test_2014_profile_rejects_2024_origin_feat() -> None:
    data = _profile_2014().model_dump()
    data["origin_feat_id"] = "savage-attacker"
    data["origin_feat_name"] = "Savage Attacker"

    with pytest.raises(ValidationError, match="origin feat"):
        CharacterBuildProfile.model_validate(data)


def test_build_audit_blocks_cross_edition_runtime_binding() -> None:
    template = build_brom_ironmark()
    profile = _profile_2014()

    issues = audit_character_build(profile, template)

    assert "runtime-ruleset-mismatch" in issues
