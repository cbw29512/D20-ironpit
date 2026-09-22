from __future__ import annotations

from app.content.audited_rogue import build_mara_quickstep_level, unsupported_mara_rogue_features
from app.content.certified_heroes import build_certified_hero_registry
from app.content.rogue_combat_fingerprint import build_mara_quickstep_level12_combat_profile
from app.content.rogue_high_progression_profile import build_mara_quickstep_level12_profile


def test_2024_rogue_level12_is_level11_plus_constitution_asi() -> None:
    level11 = build_mara_quickstep_level(11)
    template = build_mara_quickstep_level(12)

    assert unsupported_mara_rogue_features(12) == ()
    assert template.id == "mara-quickstep-l12"
    assert template.level == 12
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.constitution) == (20, 20)
    assert (level11.ability_scores.dexterity, level11.ability_scores.constitution) == (20, 18)
    assert (template.armor_class, template.max_hp, template.initiative_bonus) == (16, 123, 5)
    assert template.max_hp - level11.max_hp == 21
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (9, 5)
    assert template.saving_throw_bonuses["dexterity"] == 9
    assert template.saving_throw_bonuses["constitution"] == 5
    assert template.skill_bonuses == {"athletics": 5, "acrobatics": 9}
    assert template.progression_features.sneak_attack_d6 == 6
    assert template.progression_features.cunning_strike_trip_die_cost == 1
    assert template.progression_features.cunning_strike_max_effects == 2
    assert template.progression_features.uncanny_dodge is True
    assert template.progression_features.evasion is True
    assert {item.id: item.max_uses for item in template.resources}["adrenaline-rush"] == 4
    assert "Rogue 12" in template.source


def test_2024_rogue_level12_profile_records_full_cumulative_asi_chain() -> None:
    profile = build_mara_quickstep_level12_profile()
    assert profile.level == 12
    assert (profile.final_ability_scores.dexterity, profile.final_ability_scores.constitution) == (20, 20)
    increases = [(item.ability, item.amount) for item in profile.advancement_increases]
    assert increases == [
        ("dexterity", 1), ("constitution", 1),
        ("dexterity", 2), ("constitution", 2), ("constitution", 2),
    ]
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l12"].combat_relevant is True
    assert audits["ability-score-improvement-l12"].automated is True
    assert audits["improved-cunning-strike"].automated is True


def test_2024_rogue_level12_fingerprint_and_registry_match_runtime() -> None:
    fingerprint = build_mara_quickstep_level12_combat_profile()
    assert (fingerprint.abilities.dexterity, fingerprint.abilities.constitution) == (20, 20)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.sneak_attack_d6) == (16, 123, 6)
    assert ("adrenaline-rush", 4) in fingerprint.resources

    registry = build_certified_hero_registry()
    assert registry[("rogue", 12, "canonical")] == ("Mara Quickstep", "mara-quickstep-l12")
