from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, mara_rogue_features, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level18_combat_profile
from app.content.rogue_final_progression_profile import build_mara_quickstep_level18_profile
from app.content.rogue_thief_2014_runtime import build_mara_quickstep_2014


def test_2024_rogue_level18_reuses_universal_elusive_advantage_suppression() -> None:
    level17 = build_mara_quickstep_level(17)
    template = build_mara_quickstep_level(18)
    legacy = build_mara_quickstep_2014(18)

    assert unsupported_mara_rogue_features(18) == ()
    assert template.level == 18
    assert template.max_hp == 183
    assert template.max_hp - level17.max_hp == 10
    assert template.progression_features.sneak_attack_d6 == 9
    assert "elusive" in mara_rogue_features(18)
    assert template.progression_features.suppress_attack_advantage_while_not_incapacitated is True
    assert (
        template.progression_features.suppress_attack_advantage_while_not_incapacitated
        == legacy.progression_features.suppress_attack_advantage_while_not_incapacitated
    )


def test_2024_rogue_level18_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level18_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert profile.level == 18
    assert audits["elusive"].combat_relevant is True
    assert audits["elusive"].automated is True
    assert "universal attack-advantage suppression primitive" in (audits["elusive"].notes or "")

    fingerprint = build_mara_quickstep_level18_combat_profile()
    assert fingerprint.max_hp == 183
    assert fingerprint.sneak_attack_d6 == 9
    assert fingerprint.abilities.wisdom == 12

    registry = build_certified_hero_registry()
    assert registry[("rogue", 18, "canonical")] == ("Mara Quickstep", "mara-quickstep-l18")
