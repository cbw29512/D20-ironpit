from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.rogue_progression_profile import build_mara_quickstep_level2_profile
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level2_combat_profile


def test_2024_rogue_level2_has_cunning_action_and_expected_stats() -> None:
    try:
        template = build_mara_quickstep_level(2)
    except Exception as exc:
        raise AssertionError("2024 Rogue level 2 template must build cleanly.") from exc

    assert unsupported_mara_rogue_features(2) == ()
    assert template.id == "mara-quickstep-l2"
    assert template.level == 2
    assert template.max_hp == 17
    assert template.progression_features.sneak_attack_d6 == 1
    assert template.progression_features.cunning_action is True


def test_2024_rogue_level2_profile_and_fingerprint_match_runtime() -> None:
    try:
        profile = build_mara_quickstep_level2_profile()
        fingerprint = build_mara_quickstep_level2_combat_profile()
    except Exception as exc:
        raise AssertionError("2024 Rogue level 2 certification data must build cleanly.") from exc

    assert profile.template_id == "mara-quickstep-l2"
    assert profile.level == 2
    assert any(feature.feature_id == "cunning-action" and feature.automated for feature in profile.feature_audits)
    assert fingerprint.template_id == "mara-quickstep-l2"
    assert fingerprint.max_hp == 17
    assert fingerprint.sneak_attack_d6 == 1


def test_2024_rogue_level2_is_registered_for_certification() -> None:
    try:
        registry = build_certified_hero_registry()
    except Exception as exc:
        raise AssertionError("Certified hero registry must build with Rogue level 2.") from exc

    assert registry[("rogue", 2, "canonical")] == ("Mara Quickstep", "mara-quickstep-l2")
