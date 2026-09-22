from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level6_combat_profile
from app.content.rogue_mid_progression_profile import build_mara_quickstep_level6_profile


def test_2024_rogue_level6_is_level5_plus_hp_and_arena_inert_expertise() -> None:
    """Level 6 must preserve level 5 and add only its researched Expertise/HP delta."""
    template = build_mara_quickstep_level(6)
    assert unsupported_mara_rogue_features(6) == ()
    assert template.id == "mara-quickstep-l6"
    assert template.level == 6
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (18, 16)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (15, 51, 4)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (7, 4)
    assert template.saving_throw_bonuses["dexterity"] == 7
    assert template.skill_bonuses == {"athletics": 4, "acrobatics": 7}
    assert template.progression_features.sneak_attack_d6 == 3
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.uncanny_dodge is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 3


def test_2024_rogue_level6_profile_records_expertise_without_fake_combat_math() -> None:
    profile = build_mara_quickstep_level6_profile()
    assert profile.level == 6
    assert (profile.final_ability_scores.dexterity, profile.final_ability_scores.constitution) == (18, 16)
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["expertise-l6"].combat_relevant is False
    assert audits["expertise-l6"].automated is False
    assert "Perception and Intimidation" in (audits["expertise-l6"].notes or "")


def test_2024_rogue_level6_fingerprint_and_registry_match() -> None:
    fingerprint = build_mara_quickstep_level6_combat_profile()
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (15, 51, 3)
    assert ("adrenaline-rush", 3) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 6, "canonical")] == ("Mara Quickstep", "mara-quickstep-l6")
