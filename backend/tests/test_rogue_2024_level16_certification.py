from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level16_combat_profile
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level16_profile


def test_2024_rogue_level16_applies_only_wisdom_asi_delta() -> None:
    level15 = build_mara_quickstep_level(15)
    template = build_mara_quickstep_level(16)

    assert unsupported_mara_rogue_features(16) == ()
    assert template.level == 16
    assert template.ability_scores is not None
    assert template.ability_scores.wisdom == 12
    assert template.ability_scores.dexterity == 20
    assert template.ability_scores.constitution == 20
    assert template.max_hp == 163
    assert template.max_hp - level15.max_hp == 10
    assert template.saving_throw_bonuses["wisdom"] == 6
    assert template.saving_throw_bonuses["charisma"] == 5
    assert template.progression_features.sneak_attack_d6 == 8
    assert template.progression_features.cunning_strike_obscure_die_cost == 3
    grants = template.progression_features.saving_throw_proficiency_grants
    assert len(grants) == 1
    assert grants[0].source_id == "slippery-mind"
    assert grants[0].abilities == ["wisdom", "charisma"]


def test_2024_rogue_level16_profile_fingerprint_and_registry_match() -> None:
    profile = build_mara_quickstep_level16_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert profile.level == 16
    assert profile.final_ability_scores.wisdom == 12
    assert audits["ability-score-improvement-l16"].combat_relevant is True
    assert audits["ability-score-improvement-l16"].automated is True

    fingerprint = build_mara_quickstep_level16_combat_profile()
    assert fingerprint.abilities.wisdom == 12
    assert fingerprint.save_proficiencies == ("dexterity", "intelligence", "wisdom", "charisma")
    assert fingerprint.max_hp == 163
    assert fingerprint.sneak_attack_d6 == 8

    registry = build_certified_hero_registry()
    assert registry[("rogue", 16, "canonical")] == ("Mara Quickstep", "mara-quickstep-l16")
