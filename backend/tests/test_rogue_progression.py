from __future__ import annotations

import pytest

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_templates
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.rogue_progression_profile import build_mara_quickstep_level2_profile


def test_rogue_level2_compiles_with_cunning_action_arena_neutral() -> None:
    assert unsupported_mara_rogue_features(2) == ()

    template = build_mara_quickstep_level(2)

    assert template.id == "mara-quickstep-l2"
    assert template.level == 2
    assert template.max_hp == 17
    assert template.armor_class == 14
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (5, 3)
    assert template.progression_features.sneak_attack_d6 == 1
    assert {resource.id: resource.max_uses for resource in template.resources}["adrenaline-rush"] == 2


def test_rogue_level2_profile_audits_cunning_action_as_arena_neutral() -> None:
    profile = build_mara_quickstep_level2_profile()
    cunning_action = next(audit for audit in profile.feature_audits if audit.feature_id == "cunning-action")

    assert profile.class_levels == {"rogue": 2}
    assert cunning_action.combat_relevant is False
    assert cunning_action.automated is True


def test_rogue_level2_combat_fingerprint_matches_runtime_template() -> None:
    template = build_mara_quickstep_level(2)
    fingerprint = build_pregen_combat_profiles()["mara-quickstep-l2"]

    assert fingerprint.level == template.level
    assert fingerprint.max_hp == template.max_hp
    assert fingerprint.armor_class == template.armor_class
    assert fingerprint.sneak_attack_d6 == template.progression_features.sneak_attack_d6


def test_rogue_level3_fails_closed_until_steady_aim_is_supported() -> None:
    with pytest.raises(ValueError, match="steady-aim"):
        build_mara_quickstep_level(3)


def test_certified_catalog_contains_rogue_level2() -> None:
    certified_ids = {template.id for template in build_certified_hero_templates()}

    assert "mara-quickstep-l2" in certified_ids
