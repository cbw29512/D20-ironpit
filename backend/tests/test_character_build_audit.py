import pytest

from app.content.audited_fighter import build_karnok_stoneward
from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.pregens import build_brom_ironmark
from app.domain.character_builds import (
    AbilityIncrease,
    AbilityScores,
    CharacterBuildProfile,
    FeatureAudit,
    MagicItemAudit,
)


def _audit(
    feature_id: str,
    category: str,
    *,
    automated: bool = True,
    runtime_attack_weapon_id: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_id.replace("-", " ").title(),
        source_reference="2024 Basic Rules",
        category=category,
        combat_relevant=True,
        automated=automated,
        runtime_attack_weapon_id=runtime_attack_weapon_id,
    )


def _scores(
    strength: int,
    dexterity: int,
    constitution: int,
    intelligence: int,
    wisdom: int,
    charisma: int,
) -> AbilityScores:
    return AbilityScores(
        strength=strength,
        dexterity=dexterity,
        constitution=constitution,
        intelligence=intelligence,
        wisdom=wisdom,
        charisma=charisma,
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
        base_ability_scores=_scores(15, 13, 14, 10, 12, 8),
        background_allowed_abilities=["strength", "dexterity", "constitution"],
        background_increases=[
            AbilityIncrease(ability="strength", amount=2),
            AbilityIncrease(ability="constitution", amount=1),
        ],
        final_ability_scores=_scores(17, 13, 15, 10, 12, 8),
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
    assert profile.final_ability_scores.modifier("strength") == 3


def test_background_increases_must_follow_2024_pattern_and_allowed_scores() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.background_increases = [
        AbilityIncrease(ability="strength", amount=1),
        AbilityIncrease(ability="wisdom", amount=2),
    ]
    issues = audit_character_build(profile, template)
    assert "background-increase-uses-disallowed-ability" in issues
    assert "final-strength-does-not-match-background-increases" in issues
    assert "final-constitution-does-not-match-background-increases" in issues


def test_any_unautomated_combat_feature_blocks_raw_ready_claim() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.feature_audits[2].automated = False
    issues = audit_character_build(profile, template)
    assert "combat-feature-not-automated:savage-attacker" in issues
    with pytest.raises(ValueError, match="savage-attacker"):
        assert_character_build_raw_ready(profile, template)


def test_unautomated_combat_magic_item_blocks_raw_ready_claim() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.magic_item_audits.append(MagicItemAudit(
        item_id="plus-1-greataxe",
        item_name="+1 Greataxe",
        rarity="uncommon",
        source_reference="2024 Basic Rules: Magic Items",
        combat_relevant=True,
        automated=False,
    ))
    issues = audit_character_build(profile, template)
    assert "combat-magic-item-not-automated:plus-1-greataxe" in issues
    with pytest.raises(ValueError, match="plus-1-greataxe"):
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


def test_declared_combat_weapon_must_exist_in_runtime_attack_profiles() -> None:
    template = build_brom_ironmark()
    profile = _profile()
    profile.feature_audits.append(_audit("shortbow", "equipment", runtime_attack_weapon_id="shortbow"))
    issues = audit_character_build(profile, template)
    assert "runtime-weapon-not-automated:shortbow" in issues


def test_karnok_full_profile_passes_and_exposes_arena_weapons() -> None:
    template = build_karnok_stoneward()
    profile = build_karnok_stoneward_profile()
    assert audit_character_build(profile, template) == []
    assert_character_build_raw_ready(profile, template)
    runtime_weapon_ids = {
        template.weapon_attack.weapon.id,
        *(attack.weapon.id for attack in template.alternate_weapon_attacks),
    }
    assert runtime_weapon_ids == {"greatsword", "shortbow"}
